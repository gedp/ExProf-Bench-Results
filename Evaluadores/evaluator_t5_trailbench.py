# Extracted Evaluator Logic

import kaggle_benchmarks as kbench
import re, os, json, datetime
from collections import defaultdict

"""
T5 — MultiTarea  |  ExProf-Bench
EF: Working Memory — Dual-Task Interference
Reference: Baddeley (2000) dual-task paradigm; BRIEF-2A Working Memory scale
20 items: 5 EASY, 5 MEDIUM, 5 HARD, 5 EXTREME
"""
try:
    import matplotlib
except ImportError:
    import subprocess, sys as _sys
    subprocess.check_call([_sys.executable, '-m', 'pip', 'install', 'matplotlib', '-q'])

GLOBAL_RESULTS_T5 = []

# ── T5_TASKS_DATA — 20 items ──────────────────────────────────────────────────
# dept values: "A" → Counter A, "B" → Counter B, "BOTH" → both counters
# EXTREME items also use "critical": True  (CRITICAL override rule from tx rule_change_point)
# ground_truth: {"counter_a": int, "counter_b": int}

T5_TASKS_DATA = [
    # ─── EASY 01 ───────────────────────────────────────────────────────────────
    # A = Electronics: 850+1200+430 = 2480
    # B = Furniture:   320+480+150  = 950
    {
        "id": "t5_easy_01", "difficulty": "EASY",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-001","dept":"A","critical":False,"amount":850,
             "desc":"Laptop batch — Tech Solutions Ltd."},
            {"seq":2,"label":"INV-002","dept":"B","critical":False,"amount":320,
             "desc":"Office chairs — City Hall"},
            {"seq":3,"label":"INV-003","dept":"A","critical":False,"amount":1200,
             "desc":"Server units — DataCo"},
            {"seq":4,"label":"INV-004","dept":"B","critical":False,"amount":480,
             "desc":"Standing desks — StartupHub"},
            {"seq":5,"label":"INV-005","dept":"A","critical":False,"amount":430,
             "desc":"Tablets — MedCenter"},
            {"seq":6,"label":"INV-006","dept":"B","critical":False,"amount":150,
             "desc":"Filing cabinets — LawFirm"},
        ],
        "ground_truth": {"counter_a": 2480, "counter_b": 950},
    },
    # ─── EASY 02 ───────────────────────────────────────────────────────────────
    # A: 500+750+600 = 1850  |  B: 300+420+180 = 900
    {
        "id": "t5_easy_02", "difficulty": "EASY",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-101","dept":"A","critical":False,"amount":500,
             "desc":"Monitor batch — EduDistrict"},
            {"seq":2,"label":"INV-102","dept":"B","critical":False,"amount":300,
             "desc":"Bookshelves — PublicLibrary"},
            {"seq":3,"label":"INV-103","dept":"A","critical":False,"amount":750,
             "desc":"Network switches — FinCorp"},
            {"seq":4,"label":"INV-104","dept":"B","critical":False,"amount":420,
             "desc":"Reception desks — HotelGroup"},
            {"seq":5,"label":"INV-105","dept":"A","critical":False,"amount":600,
             "desc":"Keyboards and mice — GovOffice"},
            {"seq":6,"label":"INV-106","dept":"B","critical":False,"amount":180,
             "desc":"Coat hangers — RetailChain"},
        ],
        "ground_truth": {"counter_a": 1850, "counter_b": 900},
    },
    # ─── EASY 03 ───────────────────────────────────────────────────────────────
    # A: 1100+800+350 = 2250  |  B: 250+680+520 = 1450
    {
        "id": "t5_easy_03", "difficulty": "EASY",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-201","dept":"A","critical":False,"amount":1100,
             "desc":"Projector systems — ConferenceCenter"},
            {"seq":2,"label":"INV-202","dept":"B","critical":False,"amount":250,
             "desc":"Lounge chairs — Airport"},
            {"seq":3,"label":"INV-203","dept":"A","critical":False,"amount":800,
             "desc":"Routers — ISP Network"},
            {"seq":4,"label":"INV-204","dept":"B","critical":False,"amount":680,
             "desc":"Workbenches — ManufacturingPlant"},
            {"seq":5,"label":"INV-205","dept":"A","critical":False,"amount":350,
             "desc":"Webcams — RemoteWorkProgram"},
            {"seq":6,"label":"INV-206","dept":"B","critical":False,"amount":520,
             "desc":"Storage racks — LogisticsHub"},
        ],
        "ground_truth": {"counter_a": 2250, "counter_b": 1450},
    },
    # ─── EASY 04 ───────────────────────────────────────────────────────────────
    # A: 2000+900+650 = 3550  |  B: 400+380+220 = 1000
    {
        "id": "t5_easy_04", "difficulty": "EASY",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-301","dept":"A","critical":False,"amount":2000,
             "desc":"Data center servers — CloudCo"},
            {"seq":2,"label":"INV-302","dept":"B","critical":False,"amount":400,
             "desc":"Ergonomic chairs — HealthClinic"},
            {"seq":3,"label":"INV-303","dept":"A","critical":False,"amount":900,
             "desc":"UPS systems — BankBranch"},
            {"seq":4,"label":"INV-304","dept":"B","critical":False,"amount":380,
             "desc":"Meeting room tables — LawFirm"},
            {"seq":5,"label":"INV-305","dept":"A","critical":False,"amount":650,
             "desc":"Wireless access points — Stadium"},
            {"seq":6,"label":"INV-306","dept":"B","critical":False,"amount":220,
             "desc":"Partition panels — OpenOffice"},
        ],
        "ground_truth": {"counter_a": 3550, "counter_b": 1000},
    },
    # ─── EASY 05 ───────────────────────────────────────────────────────────────
    # A: 720+1050+480 = 2250  |  B: 600+350+750 = 1700
    {
        "id": "t5_easy_05", "difficulty": "EASY",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-401","dept":"A","critical":False,"amount":720,
             "desc":"Barcode scanners — RetailWarehouse"},
            {"seq":2,"label":"INV-402","dept":"B","critical":False,"amount":600,
             "desc":"Cafeteria tables — SchoolDistrict"},
            {"seq":3,"label":"INV-403","dept":"A","critical":False,"amount":1050,
             "desc":"Security cameras — MallGroup"},
            {"seq":4,"label":"INV-404","dept":"B","critical":False,"amount":350,
             "desc":"Outdoor benches — CityPark"},
            {"seq":5,"label":"INV-405","dept":"A","critical":False,"amount":480,
             "desc":"Handheld devices — FieldTeam"},
            {"seq":6,"label":"INV-406","dept":"B","critical":False,"amount":750,
             "desc":"Library shelving units — University"},
        ],
        "ground_truth": {"counter_a": 2250, "counter_b": 1700},
    },
    # ─── MEDIUM 01 ─────────────────────────────────────────────────────────────
    # A: 650+900+200-150+550 = 2150  |  B: 280+200+450+320 = 1250
    # BOTH amount goes to both
    {
        "id": "t5_med_01", "difficulty": "MEDIUM",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-501","dept":"A","critical":False,"amount":650,
             "desc":"Touchscreen displays — TradeShow"},
            {"seq":2,"label":"INV-502","dept":"B","critical":False,"amount":280,
             "desc":"Conference chairs — CityCouncil"},
            {"seq":3,"label":"INV-503","dept":"A","critical":False,"amount":900,
             "desc":"NAS storage units — MediaFirm"},
            {"seq":4,"label":"INV-504","dept":"BOTH","critical":False,"amount":200,
             "desc":"Shared facility insurance premium"},
            {"seq":5,"label":"INV-505","dept":"B","critical":False,"amount":450,
             "desc":"Cabinets — LegalArchives"},
            {"seq":6,"label":"INV-506","dept":"A","critical":False,"amount":-150,
             "desc":"Credit note — returned display unit"},
            {"seq":7,"label":"INV-507","dept":"B","critical":False,"amount":320,
             "desc":"Visitor chairs — Reception"},
            {"seq":8,"label":"INV-508","dept":"A","critical":False,"amount":550,
             "desc":"Wireless headsets — CallCenter"},
        ],
        "ground_truth": {"counter_a": 2150, "counter_b": 1250},
    },
    # ─── MEDIUM 02 ─────────────────────────────────────────────────────────────
    # A: 720+1100+300+480-200 = 2400  |  B: 380-100+300+550+180 = 1310
    {
        "id": "t5_med_02", "difficulty": "MEDIUM",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-601","dept":"B","critical":False,"amount":380,
             "desc":"Desks — NewHeadquarters"},
            {"seq":2,"label":"INV-602","dept":"A","critical":False,"amount":720,
             "desc":"Firewall appliances — SecureBank"},
            {"seq":3,"label":"INV-603","dept":"A","critical":False,"amount":1100,
             "desc":"Blade servers — CloudProvider"},
            {"seq":4,"label":"INV-604","dept":"B","critical":False,"amount":-100,
             "desc":"Credit note — price correction on chairs"},
            {"seq":5,"label":"INV-605","dept":"BOTH","critical":False,"amount":300,
             "desc":"Common area maintenance levy"},
            {"seq":6,"label":"INV-606","dept":"A","critical":False,"amount":480,
             "desc":"VoIP phone systems — HospitalWing"},
            {"seq":7,"label":"INV-607","dept":"B","critical":False,"amount":550,
             "desc":"Adjustable desks — ResearchLab"},
            {"seq":8,"label":"INV-608","dept":"A","critical":False,"amount":-200,
             "desc":"Vendor credit — recalled server model"},
            {"seq":9,"label":"INV-609","dept":"B","critical":False,"amount":180,
             "desc":"Storage ottomans — LoungeArea"},
        ],
        "ground_truth": {"counter_a": 2400, "counter_b": 1310},
    },
    # ─── MEDIUM 03 ─────────────────────────────────────────────────────────────
    # A: 850+150+1200+320+250-100 = 2670  |  B: 420+150-80+630+250+190 = 1560
    {
        "id": "t5_med_03", "difficulty": "MEDIUM",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-701","dept":"A","critical":False,"amount":850,
             "desc":"CCTV systems — Supermarket"},
            {"seq":2,"label":"INV-702","dept":"B","critical":False,"amount":420,
             "desc":"Display shelves — RetailStore"},
            {"seq":3,"label":"INV-703","dept":"BOTH","critical":False,"amount":150,
             "desc":"IT and facilities support contract"},
            {"seq":4,"label":"INV-704","dept":"A","critical":False,"amount":1200,
             "desc":"Storage array — DataVault"},
            {"seq":5,"label":"INV-705","dept":"B","critical":False,"amount":-80,
             "desc":"Refund — damaged chair return"},
            {"seq":6,"label":"INV-706","dept":"B","critical":False,"amount":630,
             "desc":"Modular office pods — TechCampus"},
            {"seq":7,"label":"INV-707","dept":"A","critical":False,"amount":320,
             "desc":"Smart TVs — HotelRooms"},
            {"seq":8,"label":"INV-708","dept":"BOTH","critical":False,"amount":250,
             "desc":"Annual property tax apportionment"},
            {"seq":9,"label":"INV-709","dept":"B","critical":False,"amount":190,
             "desc":"Stool sets — LabBenches"},
            {"seq":10,"label":"INV-710","dept":"A","critical":False,"amount":-100,
             "desc":"Billing reversal — duplicate invoice"},
        ],
        "ground_truth": {"counter_a": 2670, "counter_b": 1560},
    },
    # ─── MEDIUM 04 ─────────────────────────────────────────────────────────────
    # A: 450+1050+200-250+700+100 = 2250  |  B: 600+200+380-150+480+100 = 1610
    {
        "id": "t5_med_04", "difficulty": "MEDIUM",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-801","dept":"B","critical":False,"amount":600,
             "desc":"Trestle tables — EventHall"},
            {"seq":2,"label":"INV-802","dept":"A","critical":False,"amount":450,
             "desc":"Thermal printers — LogisticsFirm"},
            {"seq":3,"label":"INV-803","dept":"A","critical":False,"amount":1050,
             "desc":"Digital kiosk stations — Shopping Center"},
            {"seq":4,"label":"INV-804","dept":"BOTH","critical":False,"amount":200,
             "desc":"Shared workspace setup fee"},
            {"seq":5,"label":"INV-805","dept":"B","critical":False,"amount":380,
             "desc":"Waiting room seating — Clinic"},
            {"seq":6,"label":"INV-806","dept":"A","critical":False,"amount":-250,
             "desc":"Discount applied — bulk order kiosks"},
            {"seq":7,"label":"INV-807","dept":"B","critical":False,"amount":-150,
             "desc":"Credit note — wrong seating model"},
            {"seq":8,"label":"INV-808","dept":"A","critical":False,"amount":700,
             "desc":"POS systems — FoodChain"},
            {"seq":9,"label":"INV-809","dept":"B","critical":False,"amount":480,
             "desc":"Folding desks — TrainingRoom"},
            {"seq":10,"label":"INV-810","dept":"BOTH","critical":False,"amount":100,
             "desc":"Shared courier and logistics fee"},
        ],
        "ground_truth": {"counter_a": 2250, "counter_b": 1610},
    },
    # ─── MEDIUM 05 ─────────────────────────────────────────────────────────────
    # A: 380+760+320+900-150+180 = 2390  |  B: 520+280+320-200+180+440 = 1540
    {
        "id": "t5_med_05", "difficulty": "MEDIUM",
        "ef_primary": "Working Memory", "ef_obstacle": "Dual_Task_Interference",
        "announcement_style": "EXPLICIT_LABELS",
        "counter_a_label": "Electronics", "counter_b_label": "Furniture",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"INV-901","dept":"A","critical":False,"amount":380,
             "desc":"Label printers — WarehousingCo"},
            {"seq":2,"label":"INV-902","dept":"B","critical":False,"amount":520,
             "desc":"Boardroom chairs — CorporateHQ"},
            {"seq":3,"label":"INV-903","dept":"A","critical":False,"amount":760,
             "desc":"Interactive whiteboards — SchoolSystem"},
            {"seq":4,"label":"INV-904","dept":"B","critical":False,"amount":280,
             "desc":"Pedestal units — OpenPlanOffice"},
            {"seq":5,"label":"INV-905","dept":"BOTH","critical":False,"amount":320,
             "desc":"Office relocation shared cost"},
            {"seq":6,"label":"INV-906","dept":"A","critical":False,"amount":900,
             "desc":"Network attached printers — LargeFirm"},
            {"seq":7,"label":"INV-907","dept":"B","critical":False,"amount":-200,
             "desc":"Return credit — discontinued chair"},
            {"seq":8,"label":"INV-908","dept":"A","critical":False,"amount":-150,
             "desc":"Vendor rebate — printer order"},
            {"seq":9,"label":"INV-909","dept":"BOTH","critical":False,"amount":180,
             "desc":"Cleaning and maintenance levy"},
            {"seq":10,"label":"INV-910","dept":"B","critical":False,"amount":440,
             "desc":"Stackable chairs — AuditoriumRenovation"},
        ],
        "ground_truth": {"counter_a": 2390, "counter_b": 1540},
    },
    # ─── HARD 01 ──────────────────────────────────────────────────────────────
    # Abstract division labels. Descriptions semantically mislead to other dept.
    # ALPHA only: 1200+2400-300+850+1100 = 5250
    # BETA only:  850+1100+420-200+780   = 2950
    # BOTH:       600+400 = 1000
    # A = 5250+1000 = 6250  |  B = 2950+1000 = 3950
    {
        "id": "t5_hard_01", "difficulty": "HARD",
        "ef_primary": "Working Memory", "ef_obstacle": "Semantic_Interference",
        "announcement_style": "ABSTRACT_DIVISIONS",
        "counter_a_label": "Division Alpha", "counter_b_label": "Division Beta",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"TRF-1001","dept":"A","critical":False,"amount":1200,
             "desc":"Structural assessment — north wing (Div Alpha)"},
            {"seq":2,"label":"TRF-1002","dept":"B","critical":False,"amount":850,
             "desc":"Network infrastructure upgrade — server room (Div Beta)"},
            {"seq":3,"label":"TRF-1003","dept":"A","critical":False,"amount":2400,
             "desc":"Interior renovation contract — executive floor (Div Alpha)"},
            {"seq":4,"label":"TRF-1004","dept":"BOTH","critical":False,"amount":600,
             "desc":"Annual property insurance — all divisions"},
            {"seq":5,"label":"TRF-1005","dept":"B","critical":False,"amount":1100,
             "desc":"Diagnostic imaging equipment — radiology (Div Beta)"},
            {"seq":6,"label":"TRF-1006","dept":"A","critical":False,"amount":-300,
             "desc":"Vendor credit — returned material (Div Alpha)"},
            {"seq":7,"label":"TRF-1007","dept":"B","critical":False,"amount":420,
             "desc":"Building automation sensors (Div Beta)"},
            {"seq":8,"label":"TRF-1008","dept":"A","critical":False,"amount":850,
             "desc":"Lighting and electrical overhaul — cafeteria (Div Alpha)"},
            {"seq":9,"label":"TRF-1009","dept":"BOTH","critical":False,"amount":400,
             "desc":"Employee wellness software — all divisions"},
            {"seq":10,"label":"TRF-1010","dept":"B","critical":False,"amount":-200,
             "desc":"Warranty refund — faulty scanner (Div Beta)"},
            {"seq":11,"label":"TRF-1011","dept":"A","critical":False,"amount":1100,
             "desc":"HVAC system maintenance — lab block (Div Alpha)"},
            {"seq":12,"label":"TRF-1012","dept":"B","critical":False,"amount":780,
             "desc":"Digital signage installation — lobby (Div Beta)"},
        ],
        "ground_truth": {"counter_a": 6250, "counter_b": 3950},
    },
    # ─── HARD 02 ──────────────────────────────────────────────────────────────
    # ALPHA only: 1800+500-400+1200+900 = 4000
    # BETA only:  650+1300-250+600+400  = 2700
    # BOTH: 350+500 = 850
    # A = 4000+850 = 4850  |  B = 2700+850 = 3550
    {
        "id": "t5_hard_02", "difficulty": "HARD",
        "ef_primary": "Working Memory", "ef_obstacle": "Semantic_Interference",
        "announcement_style": "ABSTRACT_DIVISIONS",
        "counter_a_label": "Division Alpha", "counter_b_label": "Division Beta",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"TRF-2001","dept":"A","critical":False,"amount":1800,
             "desc":"Warehouse shelving system — distribution center (Div Alpha)"},
            {"seq":2,"label":"TRF-2002","dept":"B","critical":False,"amount":650,
             "desc":"Power supply units — data center (Div Beta)"},
            {"seq":3,"label":"TRF-2003","dept":"BOTH","critical":False,"amount":350,
             "desc":"Third-party audit fee — all divisions"},
            {"seq":4,"label":"TRF-2004","dept":"A","critical":False,"amount":500,
             "desc":"Loading dock equipment maintenance (Div Alpha)"},
            {"seq":5,"label":"TRF-2005","dept":"B","critical":False,"amount":1300,
             "desc":"Climate control units — storage area (Div Beta)"},
            {"seq":6,"label":"TRF-2006","dept":"A","critical":False,"amount":-400,
             "desc":"Returned goods — supplier credit (Div Alpha)"},
            {"seq":7,"label":"TRF-2007","dept":"BOTH","critical":False,"amount":500,
             "desc":"IT consulting — infrastructure review — all divisions"},
            {"seq":8,"label":"TRF-2008","dept":"A","critical":False,"amount":1200,
             "desc":"Floor tile replacement — production zone (Div Alpha)"},
            {"seq":9,"label":"TRF-2009","dept":"B","critical":False,"amount":-250,
             "desc":"Billing correction — overpayment (Div Beta)"},
            {"seq":10,"label":"TRF-2010","dept":"A","critical":False,"amount":900,
             "desc":"Plumbing overhaul — east wing (Div Alpha)"},
            {"seq":11,"label":"TRF-2011","dept":"B","critical":False,"amount":600,
             "desc":"Cabling and patch panel installation (Div Beta)"},
            {"seq":12,"label":"TRF-2012","dept":"B","critical":False,"amount":400,
             "desc":"Smart lock system — access control (Div Beta)"},
        ],
        "ground_truth": {"counter_a": 4850, "counter_b": 3550},
    },
    # ─── HARD 03 ──────────────────────────────────────────────────────────────
    # ALPHA only: 2200+800-500+1500+700 = 4700
    # BETA only:  450+1800-300+550+1000 = 3500
    # BOTH: 250+600 = 850
    # A = 4700+850 = 5550  |  B = 3500+850 = 4350
    {
        "id": "t5_hard_03", "difficulty": "HARD",
        "ef_primary": "Working Memory", "ef_obstacle": "Semantic_Interference",
        "announcement_style": "ABSTRACT_DIVISIONS",
        "counter_a_label": "Division Alpha", "counter_b_label": "Division Beta",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"TRF-3001","dept":"B","critical":False,"amount":450,
             "desc":"Conveyor belt inspection report (Div Beta)"},
            {"seq":2,"label":"TRF-3002","dept":"A","critical":False,"amount":2200,
             "desc":"Piping replacement — chemical processing unit (Div Alpha)"},
            {"seq":3,"label":"TRF-3003","dept":"BOTH","critical":False,"amount":250,
             "desc":"Safety compliance audit — all divisions"},
            {"seq":4,"label":"TRF-3004","dept":"B","critical":False,"amount":1800,
             "desc":"High-bay crane service contract (Div Beta)"},
            {"seq":5,"label":"TRF-3005","dept":"A","critical":False,"amount":800,
             "desc":"Insulation upgrade — cold storage (Div Alpha)"},
            {"seq":6,"label":"TRF-3006","dept":"A","critical":False,"amount":-500,
             "desc":"Refund — overpayment to contractor (Div Alpha)"},
            {"seq":7,"label":"TRF-3007","dept":"B","critical":False,"amount":-300,
             "desc":"Credit note — billing discrepancy (Div Beta)"},
            {"seq":8,"label":"TRF-3008","dept":"A","critical":False,"amount":1500,
             "desc":"Flooring resurfacing — workshop (Div Alpha)"},
            {"seq":9,"label":"TRF-3009","dept":"BOTH","critical":False,"amount":600,
             "desc":"Utility billing — shared infrastructure"},
            {"seq":10,"label":"TRF-3010","dept":"B","critical":False,"amount":550,
             "desc":"Forklift maintenance service (Div Beta)"},
            {"seq":11,"label":"TRF-3011","dept":"A","critical":False,"amount":700,
             "desc":"Roof repair — sector 4 building (Div Alpha)"},
            {"seq":12,"label":"TRF-3012","dept":"B","critical":False,"amount":1000,
             "desc":"Fire suppression system testing (Div Beta)"},
        ],
        "ground_truth": {"counter_a": 5550, "counter_b": 4350},
    },
    # ─── HARD 04 ──────────────────────────────────────────────────────────────
    # ALPHA only: 1600+1000-450+900+1200 = 4250
    # BETA only:  750+1400-200+300+600   = 2850
    # BOTH: 400+300 = 700
    # A = 4250+700 = 4950  |  B = 2850+700 = 3550
    {
        "id": "t5_hard_04", "difficulty": "HARD",
        "ef_primary": "Working Memory", "ef_obstacle": "Semantic_Interference",
        "announcement_style": "ABSTRACT_DIVISIONS",
        "counter_a_label": "Division Alpha", "counter_b_label": "Division Beta",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"TRF-4001","dept":"A","critical":False,"amount":1600,
             "desc":"Generator servicing — backup power facility (Div Alpha)"},
            {"seq":2,"label":"TRF-4002","dept":"BOTH","critical":False,"amount":400,
             "desc":"Shared telecommunications contract"},
            {"seq":3,"label":"TRF-4003","dept":"B","critical":False,"amount":750,
             "desc":"Precision measurement tools — calibration lab (Div Beta)"},
            {"seq":4,"label":"TRF-4004","dept":"A","critical":False,"amount":1000,
             "desc":"Steel structure inspection — bridge access (Div Alpha)"},
            {"seq":5,"label":"TRF-4005","dept":"B","critical":False,"amount":1400,
             "desc":"Hydraulic press maintenance — production (Div Beta)"},
            {"seq":6,"label":"TRF-4006","dept":"A","critical":False,"amount":-450,
             "desc":"Reversal of duplicate invoice (Div Alpha)"},
            {"seq":7,"label":"TRF-4007","dept":"BOTH","critical":False,"amount":300,
             "desc":"External legal advisory — operations — all divisions"},
            {"seq":8,"label":"TRF-4008","dept":"B","critical":False,"amount":-200,
             "desc":"Credit adjustment — price correction (Div Beta)"},
            {"seq":9,"label":"TRF-4009","dept":"A","critical":False,"amount":900,
             "desc":"Foundation waterproofing — building 3 (Div Alpha)"},
            {"seq":10,"label":"TRF-4010","dept":"B","critical":False,"amount":300,
             "desc":"Process control software licenses (Div Beta)"},
            {"seq":11,"label":"TRF-4011","dept":"A","critical":False,"amount":1200,
             "desc":"Ventilation system upgrade — east wing (Div Alpha)"},
            {"seq":12,"label":"TRF-4012","dept":"B","critical":False,"amount":600,
             "desc":"Overhead crane certification renewal (Div Beta)"},
        ],
        "ground_truth": {"counter_a": 4950, "counter_b": 3550},
    },
    # ─── HARD 05 ──────────────────────────────────────────────────────────────
    # ALPHA only: 2500+700-600+1100+800 = 4500
    # BETA only:  900+1600-400+500+700  = 3300
    # BOTH: 450+350 = 800
    # A = 4500+800 = 5300  |  B = 3300+800 = 4100
    {
        "id": "t5_hard_05", "difficulty": "HARD",
        "ef_primary": "Working Memory", "ef_obstacle": "Semantic_Interference",
        "announcement_style": "ABSTRACT_DIVISIONS",
        "counter_a_label": "Division Alpha", "counter_b_label": "Division Beta",
        "rule_change_point": None,
        "transactions": [
            {"seq":1,"label":"TRF-5001","dept":"B","critical":False,"amount":900,
             "desc":"Robotic arm calibration — assembly line (Div Beta)"},
            {"seq":2,"label":"TRF-5002","dept":"A","critical":False,"amount":2500,
             "desc":"Structural steel replacement — east tower (Div Alpha)"},
            {"seq":3,"label":"TRF-5003","dept":"BOTH","critical":False,"amount":450,
             "desc":"ISO 9001 certification renewal — all divisions"},
            {"seq":4,"label":"TRF-5004","dept":"B","critical":False,"amount":1600,
             "desc":"CNC machine servicing — manufacturing floor (Div Beta)"},
            {"seq":5,"label":"TRF-5005","dept":"A","critical":False,"amount":700,
             "desc":"Window sealing — administrative block (Div Alpha)"},
            {"seq":6,"label":"TRF-5006","dept":"BOTH","critical":False,"amount":350,
             "desc":"Annual health and safety training — all divisions"},
            {"seq":7,"label":"TRF-5007","dept":"A","critical":False,"amount":-600,
             "desc":"Returned material — storeroom credit (Div Alpha)"},
            {"seq":8,"label":"TRF-5008","dept":"B","critical":False,"amount":-400,
             "desc":"Service credit — SLA penalty (Div Beta)"},
            {"seq":9,"label":"TRF-5009","dept":"A","critical":False,"amount":1100,
             "desc":"Electrical grid overhaul — sector B (Div Alpha)"},
            {"seq":10,"label":"TRF-5010","dept":"B","critical":False,"amount":500,
             "desc":"Automated testing equipment rental (Div Beta)"},
            {"seq":11,"label":"TRF-5011","dept":"A","critical":False,"amount":800,
             "desc":"Painting and surface treatment — south facade (Div Alpha)"},
            {"seq":12,"label":"TRF-5012","dept":"B","critical":False,"amount":700,
             "desc":"Conveyor maintenance — packaging unit (Div Beta)"},
        ],
        "ground_truth": {"counter_a": 5300, "counter_b": 4100},
    },
    # ─── EXTREME 01 ───────────────────────────────────────────────────────────
    # rule_change_point = 9 → from tx 9, CRITICAL items → Counter A regardless of dept
    # tx 1-8 standard: A(DEPT-1): 1800+2200+1100-600 = 4500 | B(DEPT-2): 950-400+750+1300=2600
    # tx 9-15 with CRITICAL→A:
    #   9: DEPT-2 CRITICAL → A +1500 → A=6000
    #   10: DEPT-1 → A +900 → A=6900
    #   11: DEPT-2 → B +680 → B=3280
    #   12: DEPT-1 CRITICAL → A +2100 → A=9000
    #   13: DEPT-2 CRITICAL → A +800 → A=9800
    #   14: DEPT-2 → B +450 → B=3730
    #   15: DEPT-1 → A +1200 → A=11000
    # Final: A=11000  B=3730
    {
        "id": "t5_extreme_01", "difficulty": "EXTREME",
        "ef_primary": "Working Memory", "ef_obstacle": "Rule_Shift_Under_Load",
        "announcement_style": "RULE_CHANGE_MID_SEQUENCE",
        "counter_a_label": "DEPT-1", "counter_b_label": "DEPT-2",
        "rule_change_point": 9,
        "transactions": [
            {"seq":1,"label":"TRF-6001","dept":"A","critical":False,"amount":1800,
             "desc":"Facility expansion — phase 1 (DEPT-1)"},
            {"seq":2,"label":"TRF-6002","dept":"B","critical":False,"amount":950,
             "desc":"Equipment procurement — batch A (DEPT-2)"},
            {"seq":3,"label":"TRF-6003","dept":"A","critical":False,"amount":2200,
             "desc":"Infrastructure upgrade — east wing (DEPT-1)"},
            {"seq":4,"label":"TRF-6004","dept":"B","critical":False,"amount":-400,
             "desc":"Billing credit — corrected invoice (DEPT-2)"},
            {"seq":5,"label":"TRF-6005","dept":"A","critical":False,"amount":1100,
             "desc":"Process automation rollout (DEPT-1)"},
            {"seq":6,"label":"TRF-6006","dept":"B","critical":False,"amount":750,
             "desc":"Maintenance contract renewal (DEPT-2)"},
            {"seq":7,"label":"TRF-6007","dept":"A","critical":False,"amount":-600,
             "desc":"Reversal of duplicate entry (DEPT-1)"},
            {"seq":8,"label":"TRF-6008","dept":"B","critical":False,"amount":1300,
             "desc":"Supplier advance payment (DEPT-2)"},
            {"seq":9,"label":"TRF-6009","dept":"B","critical":True,"amount":1500,
             "desc":"Emergency system replacement — critical infrastructure (DEPT-2, CRITICAL)"},
            {"seq":10,"label":"TRF-6010","dept":"A","critical":False,"amount":900,
             "desc":"Standard procurement (DEPT-1)"},
            {"seq":11,"label":"TRF-6011","dept":"B","critical":False,"amount":680,
             "desc":"Routine maintenance order (DEPT-2)"},
            {"seq":12,"label":"TRF-6012","dept":"A","critical":True,"amount":2100,
             "desc":"Critical systems overhaul — phase 2 (DEPT-1, CRITICAL)"},
            {"seq":13,"label":"TRF-6013","dept":"B","critical":True,"amount":800,
             "desc":"Emergency response equipment (DEPT-2, CRITICAL)"},
            {"seq":14,"label":"TRF-6014","dept":"B","critical":False,"amount":450,
             "desc":"Standard supply order (DEPT-2)"},
            {"seq":15,"label":"TRF-6015","dept":"A","critical":False,"amount":1200,
             "desc":"Routine capital expenditure (DEPT-1)"},
        ],
        "ground_truth": {"counter_a": 11000, "counter_b": 3730},
    },
    # ─── EXTREME 02 ───────────────────────────────────────────────────────────
    # rule_change_point = 8
    # tx 1-7: A(DEPT-1): 1500+2000-400+600=3700 | B(DEPT-2): 800-350+1100=1550
    # tx 8-15 CRITICAL→A:
    #   8: DEPT-2 CRITICAL +1800 → A=5500
    #   9: DEPT-1 +700 → A=6200
    #   10: DEPT-2 +500 → B=2050
    #   11: DEPT-1 CRITICAL +2500 → A=8700
    #   12: DEPT-2 CRITICAL +900 → A=9600
    #   13: DEPT-2 +350 → B=2400
    #   14: DEPT-1 +1100 → A=10700
    #   15: DEPT-2 CRITICAL +600 → A=11300
    # Final: A=11300  B=2400
    {
        "id": "t5_extreme_02", "difficulty": "EXTREME",
        "ef_primary": "Working Memory", "ef_obstacle": "Rule_Shift_Under_Load",
        "announcement_style": "RULE_CHANGE_MID_SEQUENCE",
        "counter_a_label": "DEPT-1", "counter_b_label": "DEPT-2",
        "rule_change_point": 8,
        "transactions": [
            {"seq":1,"label":"TRF-7001","dept":"A","critical":False,"amount":1500,
             "desc":"Capital allocation — Q1 (DEPT-1)"},
            {"seq":2,"label":"TRF-7002","dept":"B","critical":False,"amount":800,
             "desc":"Operational expenses — Q1 (DEPT-2)"},
            {"seq":3,"label":"TRF-7003","dept":"A","critical":False,"amount":2000,
             "desc":"Annual equipment budget (DEPT-1)"},
            {"seq":4,"label":"TRF-7004","dept":"B","critical":False,"amount":-350,
             "desc":"Credit note — overpayment Q4 (DEPT-2)"},
            {"seq":5,"label":"TRF-7005","dept":"A","critical":False,"amount":-400,
             "desc":"Vendor rebate received (DEPT-1)"},
            {"seq":6,"label":"TRF-7006","dept":"B","critical":False,"amount":1100,
             "desc":"Service agreement renewal (DEPT-2)"},
            {"seq":7,"label":"TRF-7007","dept":"A","critical":False,"amount":600,
             "desc":"Supplementary procurement (DEPT-1)"},
            {"seq":8,"label":"TRF-7008","dept":"B","critical":True,"amount":1800,
             "desc":"Emergency infrastructure repair (DEPT-2, CRITICAL)"},
            {"seq":9,"label":"TRF-7009","dept":"A","critical":False,"amount":700,
             "desc":"Standard order — batch 2 (DEPT-1)"},
            {"seq":10,"label":"TRF-7010","dept":"B","critical":False,"amount":500,
             "desc":"Routine supply run (DEPT-2)"},
            {"seq":11,"label":"TRF-7011","dept":"A","critical":True,"amount":2500,
             "desc":"Critical system replacement (DEPT-1, CRITICAL)"},
            {"seq":12,"label":"TRF-7012","dept":"B","critical":True,"amount":900,
             "desc":"Priority safety equipment order (DEPT-2, CRITICAL)"},
            {"seq":13,"label":"TRF-7013","dept":"B","critical":False,"amount":350,
             "desc":"Minor maintenance supplies (DEPT-2)"},
            {"seq":14,"label":"TRF-7014","dept":"A","critical":False,"amount":1100,
             "desc":"Scheduled capital expenditure (DEPT-1)"},
            {"seq":15,"label":"TRF-7015","dept":"B","critical":True,"amount":600,
             "desc":"Urgent contingency allocation (DEPT-2, CRITICAL)"},
        ],
        "ground_truth": {"counter_a": 11300, "counter_b": 2400},
    },
    # ─── EXTREME 03 ───────────────────────────────────────────────────────────
    # rule_change_point = 8
    # tx 1-7: A(DEPT-1): 1800+1100-300=2600 | B(DEPT-2): 1200+600-500+750=2050
    # tx 8-15 CRITICAL→A:
    #   8: DEPT-1 CRITICAL +2200 → A=4800
    #   9: DEPT-2 +400 → B=2450
    #   10: DEPT-2 CRITICAL +1500 → A=6300
    #   11: DEPT-1 +800 → A=7100
    #   12: DEPT-2 CRITICAL +950 → A=8050
    #   13: DEPT-1 +1300 → A=9350
    #   14: DEPT-2 +650 → B=3100
    #   15: DEPT-1 CRITICAL +1000 → A=10350
    # Final: A=10350  B=3100
    {
        "id": "t5_extreme_03", "difficulty": "EXTREME",
        "ef_primary": "Working Memory", "ef_obstacle": "Rule_Shift_Under_Load",
        "announcement_style": "RULE_CHANGE_MID_SEQUENCE",
        "counter_a_label": "DEPT-1", "counter_b_label": "DEPT-2",
        "rule_change_point": 8,
        "transactions": [
            {"seq":1,"label":"TRF-8001","dept":"B","critical":False,"amount":1200,
             "desc":"Standard procurement run (DEPT-2)"},
            {"seq":2,"label":"TRF-8002","dept":"A","critical":False,"amount":1800,
             "desc":"Capital expansion — phase A (DEPT-1)"},
            {"seq":3,"label":"TRF-8003","dept":"B","critical":False,"amount":600,
             "desc":"Supply order — batch 3 (DEPT-2)"},
            {"seq":4,"label":"TRF-8004","dept":"A","critical":False,"amount":1100,
             "desc":"Maintenance overhaul — west block (DEPT-1)"},
            {"seq":5,"label":"TRF-8005","dept":"B","critical":False,"amount":-500,
             "desc":"Supplier credit note (DEPT-2)"},
            {"seq":6,"label":"TRF-8006","dept":"A","critical":False,"amount":-300,
             "desc":"Billing reversal — data entry error (DEPT-1)"},
            {"seq":7,"label":"TRF-8007","dept":"B","critical":False,"amount":750,
             "desc":"Annual contract renewal (DEPT-2)"},
            {"seq":8,"label":"TRF-8008","dept":"A","critical":True,"amount":2200,
             "desc":"Critical infrastructure overhaul (DEPT-1, CRITICAL)"},
            {"seq":9,"label":"TRF-8009","dept":"B","critical":False,"amount":400,
             "desc":"Routine supply replenishment (DEPT-2)"},
            {"seq":10,"label":"TRF-8010","dept":"B","critical":True,"amount":1500,
             "desc":"Emergency backup power installation (DEPT-2, CRITICAL)"},
            {"seq":11,"label":"TRF-8011","dept":"A","critical":False,"amount":800,
             "desc":"Scheduled equipment service (DEPT-1)"},
            {"seq":12,"label":"TRF-8012","dept":"B","critical":True,"amount":950,
             "desc":"Priority containment system upgrade (DEPT-2, CRITICAL)"},
            {"seq":13,"label":"TRF-8013","dept":"A","critical":False,"amount":1300,
             "desc":"Standard capital expenditure (DEPT-1)"},
            {"seq":14,"label":"TRF-8014","dept":"B","critical":False,"amount":650,
             "desc":"Minor operational supplies (DEPT-2)"},
            {"seq":15,"label":"TRF-8015","dept":"A","critical":True,"amount":1000,
             "desc":"Critical system patch deployment (DEPT-1, CRITICAL)"},
        ],
        "ground_truth": {"counter_a": 10350, "counter_b": 3100},
    },
    # ─── EXTREME 04 ───────────────────────────────────────────────────────────
    # rule_change_point = 7
    # tx 1-6: A(DEPT-1): 2100+1400+800=4300 | B(DEPT-2): 900-600+1500=1800
    # tx 7-15 CRITICAL→A:
    #   7: DEPT-2 CRITICAL +1600 → A=5900 B=1800
    #   8: DEPT-1 +500 → A=6400
    #   9: DEPT-2 +300 → B=2100
    #   10: DEPT-2 CRITICAL +2000 → A=8400
    #   11: DEPT-1 +1100 → A=9500
    #   12: DEPT-2 +450 → B=2550
    #   13: DEPT-1 CRITICAL +1800 → A=11300
    #   14: DEPT-2 CRITICAL +700 → A=12000
    #   15: DEPT-1 +900 → A=12900
    # Final: A=12900  B=2550
    {
        "id": "t5_extreme_04", "difficulty": "EXTREME",
        "ef_primary": "Working Memory", "ef_obstacle": "Rule_Shift_Under_Load",
        "announcement_style": "RULE_CHANGE_MID_SEQUENCE",
        "counter_a_label": "DEPT-1", "counter_b_label": "DEPT-2",
        "rule_change_point": 7,
        "transactions": [
            {"seq":1,"label":"TRF-9001","dept":"A","critical":False,"amount":2100,
             "desc":"Major system deployment — phase 1 (DEPT-1)"},
            {"seq":2,"label":"TRF-9002","dept":"B","critical":False,"amount":900,
             "desc":"Regular supply procurement (DEPT-2)"},
            {"seq":3,"label":"TRF-9003","dept":"A","critical":False,"amount":1400,
             "desc":"Equipment refresh cycle (DEPT-1)"},
            {"seq":4,"label":"TRF-9004","dept":"B","critical":False,"amount":-600,
             "desc":"Credit reversal — billing error (DEPT-2)"},
            {"seq":5,"label":"TRF-9005","dept":"A","critical":False,"amount":800,
             "desc":"Supplemental budget allocation (DEPT-1)"},
            {"seq":6,"label":"TRF-9006","dept":"B","critical":False,"amount":1500,
             "desc":"Contract extension payment (DEPT-2)"},
            {"seq":7,"label":"TRF-9007","dept":"B","critical":True,"amount":1600,
             "desc":"Emergency repair — primary systems (DEPT-2, CRITICAL)"},
            {"seq":8,"label":"TRF-9008","dept":"A","critical":False,"amount":500,
             "desc":"Standard operational order (DEPT-1)"},
            {"seq":9,"label":"TRF-9009","dept":"B","critical":False,"amount":300,
             "desc":"Routine supply top-up (DEPT-2)"},
            {"seq":10,"label":"TRF-9010","dept":"B","critical":True,"amount":2000,
             "desc":"Critical capacity expansion (DEPT-2, CRITICAL)"},
            {"seq":11,"label":"TRF-9011","dept":"A","critical":False,"amount":1100,
             "desc":"Planned maintenance project (DEPT-1)"},
            {"seq":12,"label":"TRF-9012","dept":"B","critical":False,"amount":450,
             "desc":"Minor supply procurement (DEPT-2)"},
            {"seq":13,"label":"TRF-9013","dept":"A","critical":True,"amount":1800,
             "desc":"Critical infrastructure upgrade (DEPT-1, CRITICAL)"},
            {"seq":14,"label":"TRF-9014","dept":"B","critical":True,"amount":700,
             "desc":"Urgent safety compliance order (DEPT-2, CRITICAL)"},
            {"seq":15,"label":"TRF-9015","dept":"A","critical":False,"amount":900,
             "desc":"Final quarter allocation (DEPT-1)"},
        ],
        "ground_truth": {"counter_a": 12900, "counter_b": 2550},
    },
    # ─── EXTREME 05 ───────────────────────────────────────────────────────────
    # rule_change_point = 7
    # tx 1-6: A(DEPT-1): 900+1800+1100=3800 | B(DEPT-2): 1400+700-400=1700
    # tx 7-15 CRITICAL→A:
    #   7: DEPT-1 +600 → A=4400
    #   8: DEPT-2 CRITICAL +1200 → A=5600
    #   9: DEPT-2 +800 → B=2500
    #   10: DEPT-1 CRITICAL +1700 → A=7300
    #   11: DEPT-2 CRITICAL +500 → A=7800
    #   12: DEPT-1 +1300 → A=9100
    #   13: DEPT-2 +600 → B=3100
    #   14: DEPT-2 CRITICAL +900 → A=10000
    #   15: DEPT-1 +1400 → A=11400
    # Final: A=11400  B=3100
    {
        "id": "t5_extreme_05", "difficulty": "EXTREME",
        "ef_primary": "Working Memory", "ef_obstacle": "Rule_Shift_Under_Load",
        "announcement_style": "RULE_CHANGE_MID_SEQUENCE",
        "counter_a_label": "DEPT-1", "counter_b_label": "DEPT-2",
        "rule_change_point": 7,
        "transactions": [
            {"seq":1,"label":"TRF-A001","dept":"B","critical":False,"amount":1400,
             "desc":"Q1 supply order (DEPT-2)"},
            {"seq":2,"label":"TRF-A002","dept":"A","critical":False,"amount":900,
             "desc":"Equipment procurement cycle A (DEPT-1)"},
            {"seq":3,"label":"TRF-A003","dept":"B","critical":False,"amount":700,
             "desc":"Annual maintenance contract (DEPT-2)"},
            {"seq":4,"label":"TRF-A004","dept":"A","critical":False,"amount":1800,
             "desc":"Major infrastructure investment (DEPT-1)"},
            {"seq":5,"label":"TRF-A005","dept":"B","critical":False,"amount":-400,
             "desc":"Supplier rebate — Q4 adjustment (DEPT-2)"},
            {"seq":6,"label":"TRF-A006","dept":"A","critical":False,"amount":1100,
             "desc":"Technology refresh — west campus (DEPT-1)"},
            {"seq":7,"label":"TRF-A007","dept":"A","critical":False,"amount":600,
             "desc":"Standard operational procurement (DEPT-1)"},
            {"seq":8,"label":"TRF-A008","dept":"B","critical":True,"amount":1200,
             "desc":"Emergency system stabilization (DEPT-2, CRITICAL)"},
            {"seq":9,"label":"TRF-A009","dept":"B","critical":False,"amount":800,
             "desc":"Routine resupply (DEPT-2)"},
            {"seq":10,"label":"TRF-A010","dept":"A","critical":True,"amount":1700,
             "desc":"Critical network redundancy deployment (DEPT-1, CRITICAL)"},
            {"seq":11,"label":"TRF-A011","dept":"B","critical":True,"amount":500,
             "desc":"Priority safety upgrade (DEPT-2, CRITICAL)"},
            {"seq":12,"label":"TRF-A012","dept":"A","critical":False,"amount":1300,
             "desc":"Planned capital expenditure (DEPT-1)"},
            {"seq":13,"label":"TRF-A013","dept":"B","critical":False,"amount":600,
             "desc":"Standard supply procurement (DEPT-2)"},
            {"seq":14,"label":"TRF-A014","dept":"B","critical":True,"amount":900,
             "desc":"Urgent facilities compliance order (DEPT-2, CRITICAL)"},
            {"seq":15,"label":"TRF-A015","dept":"A","critical":False,"amount":1400,
             "desc":"Final budget disbursement (DEPT-1)"},
        ],
        "ground_truth": {"counter_a": 11400, "counter_b": 3100},
    },
]


# ── VALIDATION ────────────────────────────────────────────────────────────────
def validate_t5_item(item):
    """Recompute ground_truth from transactions and assert it matches stored values."""
    rcp = item.get('rule_change_point')
    ca = 0
    cb = 0
    for tx in item['transactions']:
        d = tx['dept']
        amt = tx['amount']
        crit = tx.get('critical', False)
        if rcp and tx['seq'] >= rcp and crit:
            # CRITICAL override: goes to Counter A
            ca += amt
        elif d == 'A':
            ca += amt
        elif d == 'B':
            cb += amt
        elif d == 'BOTH':
            ca += amt
            cb += amt
    gt = item['ground_truth']
    assert ca == gt['counter_a'], (
        f"{item['id']}: computed counter_a={ca} but ground_truth={gt['counter_a']}")
    assert cb == gt['counter_b'], (
        f"{item['id']}: computed counter_b={cb} but ground_truth={gt['counter_b']}")
    return True

for item in T5_TASKS_DATA:
    validate_t5_item(item)
print(f'T5: {len(T5_TASKS_DATA)} items validated successfully')


# ── PROMPT BUILDER ────────────────────────────────────────────────────────────
def build_prompt_t5(item):
    la = item['counter_a_label']
    lb = item['counter_b_label']
    style = item['announcement_style']
    rcp = item.get('rule_change_point')

    if style == 'EXPLICIT_LABELS':
        header = (
            f"You are a billing clerk maintaining two separate departmental ledgers.\n\n"
            f"COUNTER RULES:\n"
            f"  - Counter A tracks: {la} (transactions labeled \"{la}\")\n"
            f"  - Counter B tracks: {lb} (transactions labeled \"{lb}\")\n"
            f"  - BOTH: the amount is added to BOTH Counter A and Counter B\n"
            f"  - Negative amounts are subtractions (credits/returns)\n"
            f"  - Start both counters at 0\n\n"
            f"TRANSACTION LOG:"
        )
    elif style == 'ABSTRACT_DIVISIONS':
        header = (
            f"You are an allocation controller tracking two divisional ledgers.\n\n"
            f"ALLOCATION RULES:\n"
            f"  - Counter A tracks: {la}\n"
            f"  - Counter B tracks: {lb}\n"
            f"  - BOTH: the amount is added to BOTH Counter A and Counter B\n"
            f"  - Negative amounts are credits or reversals\n"
            f"  - Start both counters at 0\n\n"
            f"TRANSACTION REGISTER:"
        )
    else:  # RULE_CHANGE_MID_SEQUENCE
        header = (
            f"You are a capital allocation manager tracking two departmental ledgers.\n\n"
            f"INITIAL RULE (transactions 1–{rcp-1}):\n"
            f"  - Counter A tracks: {la} allocations\n"
            f"  - Counter B tracks: {lb} allocations\n"
            f"  - Negative amounts are credits\n\n"
            f"RULE CHANGE effective from transaction {rcp}:\n"
            f"  Any item flagged as CRITICAL must be allocated to Counter A,\n"
            f"  regardless of its original department.\n"
            f"  Non-CRITICAL items continue to follow the original department rule.\n\n"
            f"TRANSACTION LOG:"
        )

    lines = []
    for tx in item['transactions']:
        sign = '+' if tx['amount'] >= 0 else ''
        dept_tag = tx['dept']
        crit_tag = ' [CRITICAL]' if tx.get('critical') else ''
        lines.append(
            f"  [{tx['seq']:02d}] {tx['label']} | Dept: {dept_tag}{crit_tag}"
            f" | Amount: {sign}${tx['amount']} | {tx['desc']}"
        )

    footer = (
        f"\n\nProcess ALL {len(item['transactions'])} transactions in sequence."
        f"\nReport the final value of BOTH counters after all transactions."
        f"\nReply ONLY with valid JSON:"
        f"\n{{\"counter_a\": <integer>, \"counter_b\": <integer>}}"
    )
    return header + '\n' + '\n'.join(lines) + footer


# ── EVALUATOR ─────────────────────────────────────────────────────────────────
def evaluate_t5(response, item):
    import json, re
    raw = re.sub(r'```(?:json)?\s*', '', response).replace('```', '')
    bs = raw.find('{')
    be = raw.rfind('}')
    if bs == -1 or be <= bs:
        return 0.0, 'FORMAT_ERROR', 'No JSON object found in response'
    try:
        parsed = json.loads(raw[bs:be+1])
    except Exception:
        return 0.0, 'FORMAT_ERROR', 'Invalid JSON'

    # Accept multiple key names
    ca = (parsed.get('counter_a') if parsed.get('counter_a') is not None
          else parsed.get('ledger_a') if parsed.get('ledger_a') is not None
          else parsed.get('dept_1') if parsed.get('dept_1') is not None
          else None)
    cb = (parsed.get('counter_b') if parsed.get('counter_b') is not None
          else parsed.get('ledger_b') if parsed.get('ledger_b') is not None
          else parsed.get('dept_2') if parsed.get('dept_2') is not None
          else None)

    if ca is None or cb is None:
        return 0.0, 'FORMAT_ERROR', 'Missing counter_a or counter_b in JSON'
    try:
        ca = int(ca)
        cb = int(cb)
    except (ValueError, TypeError):
        return 0.0, 'FORMAT_ERROR', 'Counter values are not integers'

    gt_a = item['ground_truth']['counter_a']
    gt_b = item['ground_truth']['counter_b']
    a_ok = (ca == gt_a)
    b_ok = (cb == gt_b)

    if a_ok and b_ok:
        return 1.0, None, f'Both correct: A={ca}, B={cb}'
    elif a_ok:
        return 0.5, 'COUNTER_B_ERROR', f'A correct ({ca}), B wrong (got {cb}, expected {gt_b})'
    elif b_ok:
        return 0.5, 'COUNTER_A_ERROR', f'B correct ({cb}), A wrong (got {ca}, expected {gt_a})'
    else:
        # Check for counter swap
        if ca == gt_b and cb == gt_a:
            return 0.0, 'COUNTER_SWAP', f'Counters swapped: got A={ca},B={cb} expected A={gt_a},B={gt_b}'
        return 0.0, 'BOTH_ERROR', f'Both wrong: A got {ca} (exp {gt_a}), B got {cb} (exp {gt_b})'


# ── LEADERBOARD ───────────────────────────────────────────────────────────────
import glob
T5_LEADERBOARD_FILE = 'exprof_t5_leaderboard.json'

def _t5_load_lb():
    entries = {}
    for fp in glob.glob('/kaggle/input/**/exprof_t5_leaderboard.json', recursive=True):
        try:
            with open(fp) as _f:
                for e in json.load(_f):
                    m = e.get('model')
                    if m and (m not in entries or e.get('timestamp','') > entries[m].get('timestamp','')):
                        entries[m] = e
        except Exception:
            pass
    if os.path.exists(T5_LEADERBOARD_FILE):
        try:
            with open(T5_LEADERBOARD_FILE) as _f:
                for e in json.load(_f):
                    m = e.get('model')
                    if m and (m not in entries or e.get('timestamp','') > entries[m].get('timestamp','')):
                        entries[m] = e
        except Exception:
            pass
    return list(entries.values())

def _t5_save_lb(entries):
    with open(T5_LEADERBOARD_FILE, 'w') as _f:
        json.dump(entries, _f, indent=2)

def _t5_render_lb(entries, current_model=None, progress=None):
    from IPython.display import HTML
    se = sorted(entries, key=lambda x: x.get('pass_rate', 0), reverse=True)
    rows = ''
    for i, e in enumerate(se):
        pr  = e.get('pass_rate', 0)
        epi = e.get('epi', 1.0)
        pc  = '#34a853' if pr >= 70 else '#ea4335'
        ec  = '#34a853' if epi <= 0.2 else '#fbbc04' if epi <= 0.4 else '#ea4335'
        ts  = e.get('timestamp','')[:16].replace('T',' ')
        ca_e = e.get('counter_a_errors', 0)
        cb_e = e.get('counter_b_errors', 0)
        rows += (
            f'<tr style="border-bottom:1px solid #e8eaed;">'
            f'<td style="padding:6px 8px;color:#5f6368;">{i+1}</td>'
            f'<td style="padding:6px 8px;font-weight:bold;">{e.get("model","")}</td>'
            f'<td style="padding:6px 8px;color:{pc};font-weight:bold;">{pr/100:.2f}</td>'
            f'<td style="padding:6px 8px;color:{ec};font-weight:bold;">{epi:.3f}</td>'
            f'<td style="padding:6px 8px;color:#ea4335;">{ca_e}</td>'
            f'<td style="padding:6px 8px;color:#fbbc04;">{cb_e}</td>'
            f''
            f'<td style="padding:6px 8px;font-size:10px;color:#9aa0a6;">{ts}</td>'
            f'</tr>'
        )
    if current_model:
        pg = f'⏳ {progress}' if progress else '⏳ starting...'
        rows += (
            f'<tr style="background:#fff8e1;">'
            f'<td>—</td><td style="font-weight:bold;color:#f9ab00;">{current_model}</td>'
            f'<td colspan="6" style="color:#f9ab00;">{pg}</td></tr>'
        )
    cnt = len(entries) + (1 if current_model else 0)
    return HTML(
        f'<div style="background:#f8f9fa;padding:16px;border-radius:10px;'
        f'border-left:6px solid #4285f4;margin:8px 0;">'
        f'<h3 style="margin:0 0 4px;color:#202124;font-size:15px;">'
        f'🧩 ExProf-Bench T5 MultiTask — Leaderboard ({cnt} model{"s" if cnt!=1 else ""})</h3>'
        f'<p style="font-size:11px;color:#5f6368;margin:0 0 10px;">'
        f'Baddeley (2000) Dual-Task · BRIEF-2A Working Memory · 20 items · 4 difficulty levels</p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:12px;">'
        f'<thead style="background:#e3edf9;"><tr>'
        f'<th style="padding:6px;">#</th>'
        f'<th style="padding:6px;text-align:left;">Model</th>'
        f'<th style="padding:6px;">Pass Rate</th>'
        f'<th style="padding:6px;">EPI</th>'
        f'<th style="padding:6px;">A-Errors</th>'
        f'<th style="padding:6px;">B-Errors</th>'
        f''
        f'<th style="padding:6px;">Timestamp</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )


# ── RESULTS IMAGE ─────────────────────────────────────────────────────────────


def _progress_html_t5(done, total, model_n):
    pct = int(done / total * 100) if total else 0
    return (
        f'<div style="font-family:sans-serif;padding:8px 12px;background:#f8f9fa;'
        f'border-radius:8px;margin:4px 0;">'
        f'<b>Evaluating {model_n}</b> — item {done}/{total} ({pct}%)'
        f'<div style="background:#e8eaed;border-radius:4px;height:6px;margin-top:6px;">'
        f'<div style="background:#4285f4;width:{pct}%;height:6px;border-radius:4px;"></div>'
        f'</div></div>'
    )

def _build_t5_chart(results, model_n, pass_rate, tvr, ca_e, cb_e):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    import io as _io
    from collections import defaultdict

    difficulties = ['EASY', 'MEDIUM', 'HARD', 'EXTREME']
    diff_pass    = {d: [] for d in difficulties}
    err_counts   = defaultdict(int)
    ef_pass      = defaultdict(list)

    for r in results:
        d = r.get('difficulty', 'UNKNOWN')
        if d in diff_pass:
            diff_pass[d].append(int(r.get('passed', False)))
        e = r.get('error_type') or 'NONE'
        err_counts[e] += 1
        ef = r.get('ef_primary', 'Unknown')
        ef_pass[ef].append(int(r.get('passed', False)))

    fig = plt.figure(figsize=(14, 9), facecolor='#f8f9fa')
    fig.suptitle(
        'ExProf-Bench T5 - MultiTask Dual-Counter\n'
        f'Model: {model_n}  |  Pass Rate: {pass_rate:.1f}%  |  TVR (EPI): {tvr:.3f}  |  A-errors: {ca_e}  |  B-errors: {cb_e}',
        fontsize=13, fontweight='bold', color='#202124', y=0.97
    )

    ax1 = fig.add_axes([0.05, 0.55, 0.55, 0.35])
    ids    = [r['id'] for r in results]
    scores = [r['score'] for r in results]
    colors = ['#34a853' if s >= 0.70 else '#ea4335' for s in scores]
    ax1.bar(range(len(ids)), scores, color=colors, edgecolor='white', linewidth=0.5)
    ax1.axhline(0.70, color='#fbbc04', linewidth=1.5, linestyle='--', label='Pass threshold (0.70)')
    ax1.set_xticks(range(len(ids)))
    ax1.set_xticklabels([iid.replace('t5_','').replace('_0','') for iid in ids], rotation=45, ha='right', fontsize=7)
    ax1.set_ylim(0, 1.15)
    ax1.set_ylabel('Score', fontsize=9)
    ax1.set_title('Per-item Score', fontsize=10, fontweight='bold', color='#202124')
    ax1.set_facecolor('white')
    ax1.spines[['top','right']].set_visible(False)
    ax1.legend(fontsize=8, frameon=False)

    ax2 = fig.add_axes([0.67, 0.55, 0.30, 0.35])
    d_labels = [d for d in difficulties if diff_pass[d]]
    d_rates  = [sum(diff_pass[d])/len(diff_pass[d])*100 for d in d_labels]
    d_colors = ['#34a853','#4285f4','#fbbc04','#ea4335'][:len(d_labels)]
    ax2.bar(d_labels, d_rates, color=d_colors, edgecolor='white', linewidth=0.5)
    ax2.axhline(70, color='#fbbc04', linewidth=1.5, linestyle='--')
    ax2.set_ylim(0, 110)
    ax2.set_ylabel('Pass %', fontsize=9)
    ax2.set_title('Pass Rate by Difficulty', fontsize=10, fontweight='bold', color='#202124')
    ax2.set_facecolor('white')
    ax2.spines[['top','right']].set_visible(False)
    for i, v in enumerate(d_rates):
        ax2.text(i, v + 2, f'{v:.0f}%', ha='center', fontsize=9, fontweight='bold', color='#202124')

    ax3 = fig.add_axes([0.05, 0.12, 0.40, 0.28])
    display_order = ['NONE', 'COUNTER_A_ERROR', 'COUNTER_B_ERROR', 'COUNTER_SWAP', 'BOTH_ERROR', 'FORMAT_ERROR']
    color_map = {
        'NONE':'#34a853', 'COUNTER_A_ERROR':'#ea4335', 'COUNTER_B_ERROR':'#fbbc04',
        'COUNTER_SWAP':'#9c27b0', 'BOTH_ERROR':'#ff6d01', 'FORMAT_ERROR':'#5f6368'
    }
    all_labels = [k for k in display_order]
    all_vals   = [err_counts.get(k, 0) for k in all_labels]
    all_cols   = [color_map.get(k, '#5f6368') for k in all_labels]
    bars = ax3.barh(all_labels, all_vals, color=all_cols, edgecolor='white', linewidth=0.5)
    ax3.set_xlabel('Count', fontsize=9)
    ax3.set_title('Error Type Breakdown', fontsize=10, fontweight='bold', color='#202124')
    ax3.set_facecolor('white')
    ax3.spines[['top','right']].set_visible(False)
    for bar, v in zip(bars, all_vals):
        if v > 0:
            ax3.text(v + 0.1, bar.get_y() + bar.get_height()/2,
                     str(v), va='center', fontsize=8, color='#202124')

    ax4 = fig.add_axes([0.52, 0.12, 0.45, 0.28])
    ax4.axis('off')
    rc = '#34a853' if pass_rate >= 70 else '#ea4335'
    tc = '#34a853' if tvr <= 0.2 else '#fbbc04' if tvr <= 0.4 else '#ea4335'
    ax4.text(0.02, 0.85, 'Summary', fontsize=12, fontweight='bold', color='#202124', transform=ax4.transAxes)
    ax4.text(0.02, 0.62, f'Pass Rate: {pass_rate:.1f}%', fontsize=24, fontweight='bold', color=rc, transform=ax4.transAxes)
    ax4.text(0.02, 0.42, f'TVR (EPI): {tvr:.3f}', fontsize=16, fontweight='bold', color=tc, transform=ax4.transAxes)
    ax4.text(0.02, 0.24, f'Counter-A errors: {ca_e}', fontsize=11, color='#ea4335', transform=ax4.transAxes)
    ax4.text(0.02, 0.14, f'Counter-B errors: {cb_e}', fontsize=11, color='#fbbc04', transform=ax4.transAxes)
    ax4.text(0.02, 0.04, f'Total items: {len(results)}', fontsize=11, color='#5f6368', transform=ax4.transAxes)

    fig.text(0.5, 0.01,
             'Baddeley (2000) Dual-Task Paradigm · BRIEF-2A Working Memory · ExProf-Bench T5',
             ha='center', fontsize=8, color='#5f6368')

    buf = _io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf

def _error_breakdown_html_t5(results):
    from collections import Counter
    counts = Counter(r.get('error_type','NONE') or 'NONE' for r in results)
    rows = ''
    for et, cnt in sorted(counts.items(), key=lambda x:-x[1]):
        passed = sum(1 for r in results if (r.get('error_type') or 'NONE')==et and r.get('passed'))
        color  = '#34a853' if et=='NONE' else '#ea4335'
        rows += (f'<tr><td style="padding:4px 10px;font-weight:bold;color:{color};">{et}</td>'
                 f'<td style="padding:4px 10px;">{passed}/{cnt}</td>'
                 f'<td style="padding:4px 10px;">{passed/cnt*100:.0f}%</td></tr>')
    return (f'<div style="font-family:sans-serif;background:#fff;border:1px solid #e8eaed;'
            f'border-radius:8px;padding:10px;margin:4px 0;">'
            f'<b>🧩 Error breakdown T5</b><table style="margin-top:6px;width:100%;">'
            f'<tr style="color:#5f6368;font-size:11px;"><th>Error Type</th><th>Passed</th><th>Rate</th></tr>'
            f'{rows}</table></div>')

@kbench.task(
    name='ExProf T5: TrailBench — Cognitive Flexibility / Set-Shifting',
    description='T5: 20 TrailBench items (5 EASY, 5 MEDIUM, 5 HARD, 5 EXTREME). Cognitive Flexibility / Set-Shifting. Trail Making Test B style. PASS: >=70%.'
)
def task_t5_trailbench(llm):
    import time
    import datetime
    from IPython.display import display, HTML, Image as IPImage

    model_n = getattr(llm, 'model_name', getattr(llm, 'name', 'model'))
    total_items = len(T5_TASKS_DATA)

    prev_lb = _t5_load_lb()
    prev_lb = [e for e in prev_lb if e.get('model') != model_n]

    lb_handle = display(_t5_render_lb(prev_lb, current_model=model_n), display_id=True)
    prog_handle = display(HTML(_progress_html_t5(0, total_items, model_n)), display_id=True)
    chart_handle = display(HTML(
        '<div style="height:40px;background:#f8f9fa;border-radius:8px;display:flex;'
        'align-items:center;justify-content:center;color:#9aa0a6;font-family:sans-serif;font-size:12px;">'
        'Chart T5 — available after all 20 items complete</div>'
    ), display_id=True)
    trap_handle = display(HTML(
        '<div style="height:30px;background:#f8f9fa;border-radius:8px;display:flex;'
        'align-items:center;justify-content:center;color:#9aa0a6;font-family:sans-serif;font-size:12px;">'
        'Error breakdown — available after completion</div>'
    ), display_id=True)

    print('─' * 65)
    print(f'  ExProf-Bench T5 — TrailBench (Cognitive Flexibility / Set-Shifting)')
    print(f'  Model: {model_n}  |  Items: {total_items}  |  PASS: >=70%')
    print('─' * 65)

    passed_count = 0
    scores_sum = 0.0

    for i, item in enumerate(T5_TASKS_DATA):
        prompt_text = build_prompt_t5(item)
        t0 = time.time()
        response = llm.prompt(prompt_text)
        t1 = time.time()
        score, error_type, reason = evaluate_t5(response, item)
        passed = score >= 0.70
        latency = round(t1 - t0, 2)

        if passed:
            passed_count += 1
        scores_sum += score

        GLOBAL_RESULTS_T5.append({
            'id': item['id'], 'task': 'T5', 'passed': passed, 'score': score,
            'error_type': error_type, 'reason': reason, 'difficulty': item['difficulty'],
            'ef_primary': item['ef_primary'], 'ef_obstacle': item['ef_obstacle'],
            'model': str(model_n), 'latency': latency,
        })

        flag = '✅' if passed else '❌'
        print(f'{flag} [{item["id"]}] {item["difficulty"]:8s} | {"PASS" if passed else "FAIL"}  score={score:.3f}  lat={latency}s')
        if score < 1.0:
            print(f'   error: {str(error_type or "none"):20s} | {str(reason)[:60]}')
        print()
        prog_handle.update(HTML(_progress_html_t5(i + 1, total_items, model_n)))

    overall_score = scores_sum / total_items
    pass_rate = (passed_count / total_items) * 100
    tvr = round(1.0 - overall_score, 3)
    ca_errors = sum(1 for r in GLOBAL_RESULTS_T5 if r.get('error_type') == 'COUNTER_A_ERROR')
    cb_errors = sum(1 for r in GLOBAL_RESULTS_T5 if r.get('error_type') == 'COUNTER_B_ERROR')

    current_entry = {
        'model': model_n, 'pass_rate': pass_rate, 'epi': tvr,
        'passed': passed_count, 'total': total_items,
        'counter_a_errors': ca_errors, 'counter_b_errors': cb_errors,
        'timestamp': datetime.datetime.now().isoformat(),
    }
    updated_lb = prev_lb + [current_entry]
    _t5_save_lb(updated_lb)
    lb_handle.update(_t5_render_lb(updated_lb))

    buf = _build_t5_chart(GLOBAL_RESULTS_T5, model_n, pass_rate, tvr, ca_errors, cb_errors)
    chart_handle.update(IPImage(data=buf.read(), format='png'))
    trap_handle.update(HTML(_error_breakdown_html_t5(GLOBAL_RESULTS_T5)))

    print('─' * 65)
    print(f'  FINAL  |  Pass Rate: {pass_rate:.1f}%  ({passed_count}/{total_items})')
    print(f'  TVR (EPI contribution): {tvr:.3f}  |  Counter-A errors: {ca_errors}  |  Counter-B errors: {cb_errors}')
    print('─' * 65)

    overall_passed = passed_count / total_items >= 0.70
    assertion_label = (
        '[T5-TRAILBENCH] Score: ' + str(round(overall_score, 3))
        + ' | ' + str(passed_count) + '/' + str(total_items)
        + ' tasks pass. Required: >=70% tasks pass.'
    )
    try:
        from IPython.utils.capture import capture_output as _cap
        with _cap(display=True):
            kbench.assertions.assert_true(overall_passed, expectation=assertion_label)
    except Exception:
        kbench.assertions.assert_true(overall_passed, expectation=assertion_label)

    return float(passed_count / len(T5_TASKS_DATA))

task_t5_trailbench.run(kbench.llm)

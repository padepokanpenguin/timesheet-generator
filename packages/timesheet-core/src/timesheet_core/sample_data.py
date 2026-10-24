"""Data contoh (JIRA_MOCK=true) agar UI dan Excel bisa dicoba tanpa Jira."""

from __future__ import annotations

from datetime import date

from timesheet_core.domain import RawJiraData, StoryInfo, SubtaskActivity


def sample_month(year: int, month: int) -> RawJiraData:
    d = lambda day: date(year, month, day)  # noqa: E731

    if month == 9:
        # Data bulan September 100% identik dengan sheet 'Copy of September' pada TimeSheet referensi
        stories = {
            "BIM-569": StoryInfo(
                "BIM-569",
                "BE - When processing the price, use the higher value "
                "between the edited price and the original price",
                "BIMC Implementation",
                1.0,
                None,
                d(1),
            ),
            "BIM-577": StoryInfo(
                "BIM-577",
                "BE - Handle Quotation Sub Item Updates (Data Changes Only)",
                "BIMC Implementation",
                2.0,
                None,
                d(2),
            ),
            "BIM-586": StoryInfo(
                "BIM-586",
                "BE - Handle Check Editable Price Before Convert Quotation to Sales Order",
                "BIMC Implementation",
                2.0,
                None,
                d(3),
            ),
            "PM2-639": StoryInfo(
                "PM2-639",
                "BE - Handle Validation For Negative Value at Price Adjustment",
                "Package Management",
                1.0,
                None,
                d(4),
            ),
            "DATA-1305": StoryInfo(
                "DATA-1305",
                "BE - Fix Master Data Management Issue",
                "Master Data Management",
                2.0,
                None,
                d(15),
            ),
            "KP2-1389": StoryInfo(
                "KP2-1389",
                "BE - Fix Formula Sales Markup and Relativity Factor Calculation",
                "Stabilization Kairos",
                1.0,
                None,
                d(7),
            ),
            "BIM-599": StoryInfo(
                "BIM-599",
                "BE - Fix Async Await Code at Recalculate Get Price",
                "BIMC Implementation",
                1.0,
                None,
                d(7),
            ),
            "KP2-1390": StoryInfo(
                "KP2-1390",
                "BE - Fix Sales Markup and Relativity Factor Calculation Issue",
                "Stabilization Kairos",
                1.0,
                None,
                d(8),
            ),
            "KP2-1393": StoryInfo(
                "KP2-1393",
                "BE - Remove Check Constrain in DDL Relativity Factor "
                "and Remove Validation Factor at upsert to be able greater than 1",
                "Stabilization Kairos",
                1.0,
                None,
                d(8),
            ),
            "KP2-1615": StoryInfo(
                "KP2-1615",
                "BE - Fix Unassign Parent Admission",
                "Stabilization Kairos",
                1.0,
                None,
                d(9),
            ),
            "KP2-1405": StoryInfo(
                "KP2-1405",
                "BE - Fix Cito Price Calculation",
                "Stabilization Kairos",
                2.0,
                None,
                d(10),
            ),
            "KP2-1408": StoryInfo(
                "KP2-1408",
                "BE - Fix Markup Numeric Factor Calculation",
                "Stabilization Kairos",
                2.0,
                None,
                d(11),
            ),
            "KP2-1409": StoryInfo(
                "KP2-1409",
                "BE - Fix InterHu Config",
                "Stabilization Kairos",
                1.0,
                None,
                d(11),
            ),
            "KP2-1417": StoryInfo(
                "KP2-1417",
                "BE - Handle Update IsActive at Item Base Price and Service Base Price",
                "Stabilization Kairos",
                1.0,
                None,
                d(14),
            ),
            "KP2-1452": StoryInfo(
                "KP2-1452",
                "BE - Add Filter Sales Price For Custom Sales Item Config",
                "Stabilization Kairos",
                1.0,
                None,
                d(15),
            ),
            "KP2-1454": StoryInfo(
                "KP2-1454",
                "BE - Fix Sonar Issue at Proforma Invoice",
                "Stabilization Kairos",
                2.0,
                None,
                d(17),
            ),
            "BIM-650": StoryInfo(
                "BIM-650",
                "BE - Create Endpoint For Validating Sales Items Before Convert To Sales Order",
                "Stabilization Kairos",
                2.0,
                None,
                d(18),
            ),
            "BIM-649": StoryInfo(
                "BIM-649",
                "BE - Add phone number at Quotation",
                "BIMC Implementation",
                2.0,
                None,
                d(21),
            ),
            "KP2-1453": StoryInfo(
                "KP2-1453",
                "BE - Remove Caching For Sales Service Base Price and Item Base Price",
                "Stabilization Kairos",
                1.0,
                None,
                d(21),
            ),
            "BIM-832": StoryInfo(
                "BIM-832",
                "BE - Create New Endpoint For Recalculate Get Price",
                "BIMC Implementation",
                2.0,
                None,
                d(23),
            ),
            "BIM-833": StoryInfo(
                "BIM-833",
                "BE - Create New Endpoint For Edit Price ArItems",
                "BIMC Implementation",
                2.0,
                None,
                d(24),
            ),
            "KP2-1560": StoryInfo(
                "KP2-1560",
                "BE - Create Endpoint For Insurance Reminder",
                "Stabilization Kairos",
                2.0,
                None,
                d(25),
            ),
            "KP2-1620": StoryInfo(
                "KP2-1620",
                "BE - Handle Rounding For Gettting Final Price per item",
                "Stabilization Kairos",
                1.0,
                None,
                d(25),
            ),
            "KP2-1594": StoryInfo(
                "KP2-1594",
                "BE - Handle Generate Local Mr No For RSUS",
                "Stabilization Kairos",
                1.0,
                None,
                d(28),
            ),
            "KP2-1593": StoryInfo(
                "KP2-1593",
                "BE - Enhance Get Editable Priec By Sales Items Billing Engine "
                "Integration To Fit with payload Billing Engine",
                "Stabilization Kairos",
                2.0,
                None,
                d(29),
            ),
            "KP2-1590": StoryInfo(
                "KP2-1590",
                "BE - Enhance Get Editable Price By Sales Items Billing Engine "
                "Looking Up To OverWrite Config",
                "Stabilization Kairos",
                2.0,
                None,
                d(30),
            ),
            "BIM-826": StoryInfo(
                "BIM-826",
                "BE - Handle Calculation Additional Markup at Billing Engine",
                "BIMC Implementation",
                1.0,
                None,
                d(30),
            ),
        }

        acts = [
            # 1 Sep
            SubtaskActivity(
                "BIM-569",
                d(1),
                "BIM-569-1",
                "development and fixing editable price for parent package "
                "to use higher package between edited price and original price",
            ),
            SubtaskActivity("BIM-569", d(1), "BIM-569-2", "development unit test"),
            SubtaskActivity(
                "BIM-577",
                d(1),
                "BIM-577-1",
                "development and fixing update quotation sub items to update changes only",
            ),
            SubtaskActivity("BIM-577", d(1), "BIM-577-2", "development unit test"),
            # 2 Sep
            SubtaskActivity(
                "BIM-577",
                d(2),
                "BIM-577-1",
                "development and fixing update quotation sub items to update changes only",
            ),
            SubtaskActivity("BIM-577", d(2), "BIM-577-2", "development unit test"),
            SubtaskActivity(
                "BIM-586",
                d(2),
                "BIM-586-1",
                "development and adding get editable price before convert quotation to sales order",
            ),
            # 3 Sep
            SubtaskActivity(
                "BIM-586",
                d(3),
                "BIM-586-1",
                "development and adding get editable price before convert quotation to sales order",
            ),
            SubtaskActivity("BIM-586", d(3), "BIM-586-2", "development unit test"),
            # 4 Sep
            SubtaskActivity(
                "PM2-639",
                d(4),
                "PM2-639-1",
                "development and fixing pricing clam for negative adjustment price",
            ),
            SubtaskActivity(
                "DATA-1305",
                d(4),
                "DATA-1305-1",
                "development and exclude audit column at kafka master data management",
            ),
            SubtaskActivity("DATA-1305", d(4), "DATA-1305-2", "development unit test"),
            # 7 Sep
            SubtaskActivity(
                "KP2-1389",
                d(7),
                "KP2-1389-1",
                "development and fixing formula for sales markup and relativity factor calculation",
            ),
            SubtaskActivity("KP2-1389", d(7), "KP2-1389-2", "development unit test"),
            SubtaskActivity(
                "BIM-599", d(7), "BIM-599-1", "development and fixing async await at recalculate get price"
            ),
            SubtaskActivity("BIM-599", d(7), "BIM-599-2", "development unit test"),
            # 8 Sep
            SubtaskActivity(
                "KP2-1390", d(8), "KP2-1390-1", "development and fixing sales markup calculation"
            ),
            SubtaskActivity("KP2-1390", d(8), "KP2-1390-2", "development unit test"),
            SubtaskActivity(
                "KP2-1393",
                d(8),
                "KP2-1393-1",
                "development query for removing constrain validation at relativity factor",
            ),
            # 9 Sep
            SubtaskActivity(
                "KP2-1615", d(9), "KP2-1615-1", "development and fixing unassign parent admission"
            ),
            SubtaskActivity("KP2-1615", d(9), "KP2-1615-2", "development unit test"),
            SubtaskActivity(
                "KP2-1405", d(9), "KP2-1405-1", "development and fixing formula cito price calculation"
            ),
            SubtaskActivity("KP2-1405", d(9), "KP2-1405-2", "development unit test"),
            # 10 Sep
            SubtaskActivity(
                "KP2-1405", d(10), "KP2-1405-1", "development and fixing formula cito price calculation"
            ),
            SubtaskActivity("KP2-1405", d(10), "KP2-1405-2", "development unit test"),
            SubtaskActivity(
                "KP2-1408", d(10), "KP2-1408-1", "development and fixing markup numeric factor calculation"
            ),
            # 11 Sep
            SubtaskActivity(
                "KP2-1408", d(11), "KP2-1408-1", "development and fixing markup numeric factor calculation"
            ),
            SubtaskActivity("KP2-1408", d(11), "KP2-1408-2", "development unit test"),
            SubtaskActivity(
                "KP2-1409", d(11), "KP2-1409-1", "development and fixing inter hu config at billing engine"
            ),
            SubtaskActivity("KP2-1409", d(11), "KP2-1409-2", "development unit test"),
            # 14 Sep
            SubtaskActivity(
                "KP2-1417",
                d(14),
                "KP2-1417-1",
                "development and fixing master data item base price and service base price",
            ),
            SubtaskActivity("KP2-1417", d(14), "KP2-1417-2", "development unit test"),
            # 15 Sep
            SubtaskActivity(
                "DATA-1305",
                d(15),
                "DATA-1305-1",
                "development and fixing insert missing table Medical.MedicalProcedure",
            ),
            SubtaskActivity("DATA-1305", d(15), "DATA-1305-2", "development unit test"),
            SubtaskActivity(
                "KP2-1452",
                d(15),
                "KP2-1452-1",
                "development and fixing sales price config to use salesPrice from admission",
            ),
            SubtaskActivity("KP2-1452", d(15), "KP2-1452-2", "development unit test"),
            # 16 Sep
            SubtaskActivity(
                "KP2-1454", d(16), "KP2-1454-1", "development and fixing sonar issue at proforma invoice"
            ),
            SubtaskActivity(
                "KP2-1454",
                d(16),
                "KP2-1454-2",
                "development and fixing whatsapp integration to whatsapp service",
            ),
            # 17 Sep
            SubtaskActivity(
                "BIM-650",
                d(17),
                "BIM-650-1",
                "development and create new endpoint for validation "
                "sales items before converting to sales order",
            ),
            SubtaskActivity("BIM-650", d(17), "BIM-650-2", "development unit test"),
            SubtaskActivity(
                "KP2-1454",
                d(17),
                "KP2-1454-1",
                "development and fixing whatsapp integration to whatsapp service",
            ),
            SubtaskActivity("KP2-1454", d(17), "KP2-1454-2", "development unit test"),
            # 18 Sep
            SubtaskActivity("BIM-649", d(18), "BIM-649-1", "development and add phone number at quotation"),
            SubtaskActivity("BIM-649", d(18), "BIM-649-2", "development unit test"),
            SubtaskActivity(
                "BIM-650",
                d(18),
                "BIM-650-1",
                "development and create new endpoint for validation "
                "sales items before converting to sales order",
            ),
            SubtaskActivity("BIM-650", d(18), "BIM-650-2", "development unit test"),
            # 21 Sep
            SubtaskActivity(
                "KP2-1453",
                d(21),
                "KP2-1453-1",
                "development and remove caching at billing engine to get new value",
            ),
            SubtaskActivity("BIM-649", d(21), "BIM-649-1", "development and add phone number at quotation"),
            SubtaskActivity("BIM-649", d(21), "BIM-649-2", "development unit test"),
            # 22 Sep
            SubtaskActivity(
                "BIM-832",
                d(22),
                "BIM-832-1",
                "development and create new endpoint for recalculate edit price",
            ),
            SubtaskActivity("BIM-832", d(22), "BIM-832-2", "EMR-7637"),
            # 23 Sep
            SubtaskActivity(
                "BIM-832",
                d(23),
                "BIM-832-1",
                "development and create new endpoint for recalculate edit price",
            ),
            SubtaskActivity("BIM-832", d(23), "BIM-832-2", "development unit test"),
            SubtaskActivity("BIM-833", d(23), "BIM-833-1", "development new endpoint for updating aritems"),
            # 24 Sep
            SubtaskActivity("BIM-833", d(24), "BIM-833-1", "development new endpoint for updating aritems"),
            SubtaskActivity("BIM-833", d(24), "BIM-833-2", "development unit test"),
            SubtaskActivity(
                "KP2-1560",
                d(24),
                "KP2-1560-1",
                "development and create new endpoint for sending insurance reminder",
            ),
            # 25 Sep
            SubtaskActivity(
                "KP2-1560",
                d(25),
                "KP2-1560-1",
                "development and create new endpoint for sending insurance reminder",
            ),
            SubtaskActivity("KP2-1560", d(25), "KP2-1560-2", "development integration to whatsapp service"),
            SubtaskActivity("KP2-1560", d(25), "KP2-1560-3", "development unit test"),
            SubtaskActivity(
                "KP2-1620", d(25), "KP2-1620-1", "development and handling rounding final price per item"
            ),
            SubtaskActivity("KP2-1620", d(25), "KP2-1620-2", "development unit test"),
            # 28 Sep
            SubtaskActivity(
                "KP2-1594",
                d(28),
                "KP2-1594-1",
                "development and redirecting organizationId from rsuslv to shlv",
            ),
            SubtaskActivity("KP2-1594", d(28), "KP2-1594-2", "development unit test"),
            SubtaskActivity(
                "KP2-1593",
                d(28),
                "KP2-1593-1",
                "development and handle get price at billing integration to receive admission_id",
            ),
            # 29 Sep
            SubtaskActivity(
                "KP2-1593",
                d(29),
                "KP2-1593-1",
                "development and handle get price at billing integration to receive admission_id",
            ),
            SubtaskActivity("KP2-1593", d(29), "KP2-1593-2", "development unit test"),
            SubtaskActivity(
                "KP2-1590",
                d(29),
                "KP2-1590-1",
                "development get editable price to look up to overwrite config",
            ),
            # 30 Sep
            SubtaskActivity(
                "KP2-1590",
                d(30),
                "KP2-1590-1",
                "development get editable price to look up to overwrite config",
            ),
            SubtaskActivity("KP2-1590", d(30), "KP2-1590-2", "development unit test"),
            SubtaskActivity("BIM-826", d(30), "BIM-826-1", "development calcultation for additional markup"),
            SubtaskActivity("BIM-826", d(30), "BIM-826-2", "development unit test"),
        ]
        return RawJiraData(activities=acts, stories=stories)

    if month == 10:
        # Data bulan Oktober penuh berbasis Subtask Development aktual Siloam
        stories = {
            "PM2-108": StoryInfo(
                "PM2-108", "Package Management - Kafka Integration", "Package Management", 2.0, None, d(1)
            ),
            "PM2-602": StoryInfo(
                "PM2-602",
                "BE - Available for Order Filter and Kit Package",
                "Package Management",
                4.0,
                None,
                d(8),
            ),
            "KP2-1578": StoryInfo(
                "KP2-1578", "Readiness Deployment & Performance Test", "Stabilization Kairos", 2.0, None, d(9)
            ),
            "BIM-976": StoryInfo(
                "BIM-976", "DEPLOYMENT CHECKLIST - PAS KAIROS", "Stabilization Kairos", 1.0, None, d(12)
            ),
            "W2-1415": StoryInfo(
                "W2-1415", "DPM Package Seeder Optimization", "DPM Integration", 1.0, None, d(13)
            ),
            "BIM-841": StoryInfo(
                "BIM-841", "BE - Price Calculation Fallback Logic", "Stabilization Kairos", 2.0, None, d(14)
            ),
            "KP2-1634": StoryInfo(
                "KP2-1634",
                "[Pricing] [Overwrite Config] Change Flow Get Price",
                "Kairos Pas",
                5.0,
                None,
                d(19),
            ),
            "KP2-1644": StoryInfo(
                "KP2-1644",
                "[Transaction] - Add validasi create SO item inactive",
                "Kairos Pas",
                6.0,
                None,
                None,
            ),
        }

        acts = [
            # Minggu 1
            SubtaskActivity("PM2-108", d(1), "PM2-229", "[MONITORING] Kafka Sink and Worker"),
            SubtaskActivity(
                "PM2-602",
                d(2),
                "PM2-641",
                "BE - Handle Filter For Procedure Kit Package at Package Variant List",
            ),
            # Minggu 2
            SubtaskActivity(
                "PM2-602", d(5), "PM2-642", "BE - Add Available For Order Filter for Variant List"
            ),
            SubtaskActivity(
                "PM2-602", d(6), "PM2-642", "BE - Add Available For Order Filter for Variant List"
            ),
            SubtaskActivity(
                "PM2-602", d(7), "PM2-642", "BE - Add Available For Order Filter for Variant List"
            ),
            SubtaskActivity(
                "PM2-602", d(8), "PM2-642", "BE - Add Available For Order Filter for Variant List"
            ),
            SubtaskActivity(
                "KP2-1578", d(9), "KP2-1637", "BE - List Deployment Checklist For Readiness Deployment"
            ),
            SubtaskActivity(
                "KP2-1578",
                d(9),
                "KP2-1636",
                "BE - Support Performance Test and Fixing Sonar Issue For Deployment",
            ),
            # Minggu 3
            SubtaskActivity("BIM-976", d(12), "BIM-976-1", "DEPLOYMENT CHECKLIST - PAS KAIROS verification"),
            SubtaskActivity("W2-1415", d(13), "W2-2861", "Seeder package variant end date null for DPM"),
            SubtaskActivity(
                "BIM-841", d(14), "BIM-988", "BE - Fix Get Editable Price to Falback Logic Legacy"
            ),
            SubtaskActivity(
                "KP2-1634",
                d(14),
                "KP2-1643",
                "BE - Handle Priority Sales Price Config on Get Price Billing Engine",
            ),
            SubtaskActivity(
                "KP2-1634",
                d(15),
                "KP2-1643",
                "BE - Handle Priority Sales Price Config on Get Price Billing Engine",
            ),
            SubtaskActivity(
                "KP2-1634",
                d(16),
                "KP2-1643",
                "BE - Handle Priority Sales Price Config on Get Price Billing Engine",
            ),
            SubtaskActivity(
                "KP2-1644", d(16), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            # Minggu 4 & 5
            SubtaskActivity(
                "KP2-1634",
                d(19),
                "KP2-1643",
                "BE - Handle Priority Sales Price Config on Get Price Billing Engine",
            ),
            SubtaskActivity(
                "KP2-1644", d(19), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(20), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(21), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(22), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(23), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(26), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(27), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(28), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(29), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
            SubtaskActivity(
                "KP2-1644", d(30), "KP2-1645", "BE - Add Validation For InActive Sales Item Organization"
            ),
        ]
        return RawJiraData(activities=acts, stories=stories)

    # Bulan lainnya (default Januari untuk unit test)
    stories = {
        "BPAS-5437": StoryInfo(
            "BPAS-5437", "BE - Optimize Query Get Admission List", "Stabilization Kairos", 5, None, d(26)
        ),
        "BPAS-5115": StoryInfo(
            "BPAS-5115", "BE - Create endpoint get patient summary", "Stabilization Kairos", 2.5, None, d(15)
        ),
        "KP2-68": StoryInfo("KP2-68", "FE - Setup design system package", "Kairos Pas", 4, None, None),
        "KP2-900": StoryInfo("KP2-900", "BE - Story tanpa Epic (contoh peringatan)", None, None, 3, None),
    }
    acts = [
        SubtaskActivity(
            "BPAS-5437", d(21), "BPAS-5438", "development filter for getting admission list data"
        ),
        SubtaskActivity("BPAS-5437", d(22), "BPAS-5439", "development unit test for get admission list"),
        SubtaskActivity("BPAS-5437", d(23), "BPAS-5440", "fixing query joining patient organization"),
        SubtaskActivity("BPAS-5437", d(26), "BPAS-5441", "code review and merge"),
        SubtaskActivity("BPAS-5115", d(14), "BPAS-5116", "development new endpoint"),
        SubtaskActivity("BPAS-5115", d(15), "BPAS-5117", "development unit test"),
        SubtaskActivity("KP2-68", d(14), "KP2-69", "setup package and build config"),
        SubtaskActivity("KP2-68", d(16), "KP2-70", "development button and input components"),
        SubtaskActivity("KP2-900", d(19), None, None),  # aktivitas langsung di story, tanpa sub-task
        SubtaskActivity("BPAS-5437", d(24), "BPAS-5442", "aktivitas Sabtu (diabaikan)"),
    ]
    return RawJiraData(activities=acts, stories=stories)

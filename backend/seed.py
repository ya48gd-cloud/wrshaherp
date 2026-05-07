"""
seed.py — بيانات تجريبية لورشة تصنيع معدات الأعلاف
Run: python seed.py
"""
import asyncio
from decimal import Decimal
from datetime import date

from app.core.database import AsyncSessionLocal
from app.models.models import (
    MaterialCategory, Material, StockMovement,
    Equipment, EquipmentDimension, BOMLine,
    WorkOrder, CostLine,
    Worker, Customer, CustomerOrder,
)


async def seed():
    async with AsyncSessionLocal() as db:

        # ── 1. تصنيفات المواد ─────────────────────────────────────
        cats = [
            MaterialCategory(name_ar="فولاذ وحديد",      name_en="Steel & Iron"),
            MaterialCategory(name_ar="هيدروليك",          name_en="Hydraulics"),
            MaterialCategory(name_ar="كهرباء وتحكم",      name_en="Electrical"),
            MaterialCategory(name_ar="مسامير وبراغي",     name_en="Fasteners"),
            MaterialCategory(name_ar="مواد استهلاكية",    name_en="Consumables"),
            MaterialCategory(name_ar="تروس وناقلات",      name_en="Gears & Drives"),
            MaterialCategory(name_ar="شاشات وتغذية",      name_en="Screens & Feeders"),
        ]
        db.add_all(cats)
        await db.flush()
        steel, hydro, elec, fast, cons, gears, screens = cats

        # ── 2. المواد ─────────────────────────────────────────────
        mats = [
            Material(code="ST-37-6MM",   name_ar="لوح فولاذ ST-37 سماكة 6mm",   name_en="Steel Plate 6mm",   unit="kg",  unit_cost=Decimal("16.00"),  stock_qty=Decimal("3000"), reorder_level=Decimal("400"), category_id=steel.id, supplier="شركة الفولاذ المتحدة"),
            Material(code="ST-52-10MM",  name_ar="لوح فولاذ ST-52 سماكة 10mm",  name_en="Steel Plate 10mm",  unit="kg",  unit_cost=Decimal("18.50"),  stock_qty=Decimal("4000"), reorder_level=Decimal("500"), category_id=steel.id, supplier="شركة الفولاذ المتحدة"),
            Material(code="PIPE-60",     name_ar="أنبوب فولاذي 60mm",            name_en="Steel Pipe 60mm",   unit="m",   unit_cost=Decimal("85.00"),  stock_qty=Decimal("150"),  reorder_level=Decimal("20"),  category_id=steel.id, supplier="مصنع الأنابيب الوطني"),
            Material(code="SQ-BAR-40",   name_ar="مقطع مربع 40×40mm",            name_en="Square Bar 40x40",  unit="m",   unit_cost=Decimal("55.00"),  stock_qty=Decimal("200"),  reorder_level=Decimal("30"),  category_id=steel.id, supplier="مصنع الحديد الوطني"),
            Material(code="HYD-PUMP-11", name_ar="طلمبة هيدروليك 11KW",          name_en="Hydraulic Pump 11KW",unit="pcs",unit_cost=Decimal("6500.00"),stock_qty=Decimal("5"),   reorder_level=Decimal("1"),   category_id=hydro.id, supplier="Parker Hannifin"),
            Material(code="HYD-CYL-80",  name_ar="أسطوانة هيدروليك 80mm",       name_en="Hydraulic Cyl 80mm",unit="pcs",unit_cost=Decimal("2800.00"),stock_qty=Decimal("8"),   reorder_level=Decimal("2"),   category_id=hydro.id, supplier="Parker Hannifin"),
            Material(code="MOTOR-15KW",  name_ar="موتور كهربائي 15KW",           name_en="Motor 15KW",        unit="pcs",unit_cost=Decimal("7200.00"),stock_qty=Decimal("6"),   reorder_level=Decimal("1"),   category_id=elec.id,  supplier="Siemens Agent"),
            Material(code="MOTOR-7KW",   name_ar="موتور كهربائي 7.5KW",          name_en="Motor 7.5KW",       unit="pcs",unit_cost=Decimal("4100.00"),stock_qty=Decimal("8"),   reorder_level=Decimal("2"),   category_id=elec.id,  supplier="Siemens Agent"),
            Material(code="INVERTER-15", name_ar="انفرتر تحكم 15KW",             name_en="VFD Inverter 15KW", unit="pcs",unit_cost=Decimal("5500.00"),stock_qty=Decimal("4"),   reorder_level=Decimal("1"),   category_id=elec.id,  supplier="Delta Electronics"),
            Material(code="GEARBOX-20",  name_ar="علبة تروس نسبة 1:20",          name_en="Gearbox 1:20",      unit="pcs",unit_cost=Decimal("3800.00"),stock_qty=Decimal("6"),   reorder_level=Decimal("1"),   category_id=gears.id, supplier="مورد التروس"),
            Material(code="BELT-B80",    name_ar="سير نقل حركة B-80",            name_en="V-Belt B80",        unit="pcs",unit_cost=Decimal("45.00"),  stock_qty=Decimal("50"),  reorder_level=Decimal("10"),  category_id=gears.id),
            Material(code="SCREEN-3MM",  name_ar="شاشة تصفية 3mm",               name_en="Sieve Screen 3mm",  unit="pcs",unit_cost=Decimal("1200.00"),stock_qty=Decimal("12"),  reorder_level=Decimal("3"),   category_id=screens.id,supplier="مصنع الشاشات"),
            Material(code="SCREEN-5MM",  name_ar="شاشة تصفية 5mm",               name_en="Sieve Screen 5mm",  unit="pcs",unit_cost=Decimal("1200.00"),stock_qty=Decimal("10"),  reorder_level=Decimal("3"),   category_id=screens.id,supplier="مصنع الشاشات"),
            Material(code="BOLT-M16",    name_ar="مسمار M16 استانلس",            name_en="Bolt M16 SS",       unit="pcs",unit_cost=Decimal("8.00"),   stock_qty=Decimal("2000"),reorder_level=Decimal("300"), category_id=fast.id),
            Material(code="WELD-ROD",    name_ar="سلك لحام E7018",               name_en="Welding Rod E7018", unit="kg", unit_cost=Decimal("35.00"),  stock_qty=Decimal("200"),  reorder_level=Decimal("40"),  category_id=cons.id),
        ]
        db.add_all(mats)
        await db.flush()
        st37,st52,pipe,sqbar,hpump,hcyl,mot15,mot75,inv,gbox,belt,scr3,scr5,bolt,weld = mats

        # ── 3. حركات أولية ───────────────────────────────────────
        mvs = [
            StockMovement(material_id=st37.id, movement_type="in", qty=Decimal("3000"), unit_cost=Decimal("16"), total_cost=Decimal("48000"), reference="PO-2024-001", movement_date=date(2024,1,5)),
            StockMovement(material_id=st52.id, movement_type="in", qty=Decimal("4000"), unit_cost=Decimal("18.50"), total_cost=Decimal("74000"), reference="PO-2024-002", movement_date=date(2024,1,5)),
            StockMovement(material_id=mot15.id,movement_type="in", qty=Decimal("6"),    unit_cost=Decimal("7200"), total_cost=Decimal("43200"), reference="PO-2024-003", movement_date=date(2024,1,10)),
        ]
        db.add_all(mvs); await db.flush()

        # ── 4. المعدات — مجرشة الأعلاف FG-500 ────────────────────
        fg = Equipment(code="FG-500", name_ar="مجرشة أعلاف 5 طن/ساعة", name_en="Feed Grinder 5T/h FG-500", description="مجرشة أعلاف مدمجة", level=0, weight_kg=Decimal("2800"), cad_drawing_no="DWG-FG500-Rev2")
        db.add(fg); await db.flush()

        grd = Equipment(code="FG500-GRD", name_ar="وحدة الطحن",           name_en="Grinding Unit",   parent_id=fg.id, level=1, weight_kg=Decimal("1100"), cad_drawing_no="DWG-GRD-001")
        scr = Equipment(code="FG500-SCR", name_ar="وحدة الغربلة",         name_en="Screening Unit",  parent_id=fg.id, level=1, weight_kg=Decimal("650"),  cad_drawing_no="DWG-SCR-001")
        fed = Equipment(code="FG500-FED", name_ar="وحدة التغذية",         name_en="Feeding Unit",    parent_id=fg.id, level=1, weight_kg=Decimal("420"),  cad_drawing_no="DWG-FED-001")
        drv = Equipment(code="FG500-DRV", name_ar="وحدة الإدارة والتشغيل",name_en="Drive System",    parent_id=fg.id, level=1, weight_kg=Decimal("380"),  cad_drawing_no="DWG-DRV-001")
        frm = Equipment(code="FG500-FRM", name_ar="الهيكل والإطار",       name_en="Main Frame",      parent_id=fg.id, level=1, weight_kg=Decimal("250"),  cad_drawing_no="DWG-FRM-001")
        db.add_all([grd,scr,fed,drv,frm]); await db.flush()

        hm  = Equipment(code="FG500-GRD-HM", name_ar="مطرقة الطحن",   name_en="Hammer Mill",    parent_id=grd.id, level=2, weight_kg=Decimal("480"), cad_drawing_no="DWG-HM-001")
        vs  = Equipment(code="FG500-SCR-VS", name_ar="شاشة اهتزازية", name_en="Vibro Screen",   parent_id=scr.id, level=2, weight_kg=Decimal("280"), cad_drawing_no="DWG-VS-001")
        sf  = Equipment(code="FG500-FED-SF", name_ar="ملولب تغذية",   name_en="Screw Feeder",   parent_id=fed.id, level=2, weight_kg=Decimal("180"), cad_drawing_no="DWG-SF-001")
        db.add_all([hm,vs,sf]); await db.flush()

        # مقاسات
        dims = [
            EquipmentDimension(equipment_id=fg.id,  dim_key="length",   dim_value="3200", unit="mm"),
            EquipmentDimension(equipment_id=fg.id,  dim_key="width",    dim_value="1800", unit="mm"),
            EquipmentDimension(equipment_id=fg.id,  dim_key="height",   dim_value="2400", unit="mm"),
            EquipmentDimension(equipment_id=fg.id,  dim_key="capacity", dim_value="5",    unit="طن/ساعة"),
            EquipmentDimension(equipment_id=fg.id,  dim_key="power",    dim_value="22.5", unit="kW"),
            EquipmentDimension(equipment_id=grd.id, dim_key="diameter", dim_value="800",  unit="mm"),
            EquipmentDimension(equipment_id=grd.id, dim_key="speed",    dim_value="2950", unit="rpm"),
            EquipmentDimension(equipment_id=scr.id, dim_key="length",   dim_value="1200", unit="mm"),
            EquipmentDimension(equipment_id=sf.id,  dim_key="diameter", dim_value="200",  unit="mm"),
        ]
        db.add_all(dims)

        # BOM
        bom = [
            BOMLine(equipment_id=grd.id, material_id=st52.id,  qty=Decimal("420"), unit_cost=Decimal("18.50"), total_cost=Decimal("7770"),  notes="لوح 10mm لجسم المطرقة"),
            BOMLine(equipment_id=grd.id, material_id=mot15.id, qty=Decimal("1"),   unit_cost=Decimal("7200"),  total_cost=Decimal("7200"),  notes="موتور رئيسي 15KW"),
            BOMLine(equipment_id=grd.id, material_id=gbox.id,  qty=Decimal("1"),   unit_cost=Decimal("3800"),  total_cost=Decimal("3800"),  notes="علبة تروس خفض"),
            BOMLine(equipment_id=grd.id, material_id=belt.id,  qty=Decimal("4"),   unit_cost=Decimal("45"),    total_cost=Decimal("180"),   notes="سيور نقل حركة"),
            BOMLine(equipment_id=grd.id, material_id=weld.id,  qty=Decimal("12"),  unit_cost=Decimal("35"),    total_cost=Decimal("420"),   notes="سلك لحام"),
            BOMLine(equipment_id=scr.id, material_id=st37.id,  qty=Decimal("180"), unit_cost=Decimal("16"),    total_cost=Decimal("2880"),  notes="هيكل الشاشة"),
            BOMLine(equipment_id=scr.id, material_id=scr3.id,  qty=Decimal("4"),   unit_cost=Decimal("1200"),  total_cost=Decimal("4800"),  notes="شاشات 3mm"),
            BOMLine(equipment_id=scr.id, material_id=scr5.id,  qty=Decimal("2"),   unit_cost=Decimal("1200"),  total_cost=Decimal("2400"),  notes="شاشات 5mm"),
            BOMLine(equipment_id=scr.id, material_id=mot75.id, qty=Decimal("1"),   unit_cost=Decimal("4100"),  total_cost=Decimal("4100"),  notes="موتور اهتزاز"),
            BOMLine(equipment_id=fed.id, material_id=pipe.id,  qty=Decimal("8"),   unit_cost=Decimal("85"),    total_cost=Decimal("680"),   notes="أنابيب ملولب"),
            BOMLine(equipment_id=fed.id, material_id=hcyl.id,  qty=Decimal("2"),   unit_cost=Decimal("2800"),  total_cost=Decimal("5600"),  notes="أسطوانات هيدروليك"),
            BOMLine(equipment_id=drv.id, material_id=inv.id,   qty=Decimal("1"),   unit_cost=Decimal("5500"),  total_cost=Decimal("5500"),  notes="انفرتر تحكم في السرعة"),
            BOMLine(equipment_id=drv.id, material_id=hpump.id, qty=Decimal("1"),   unit_cost=Decimal("6500"),  total_cost=Decimal("6500"),  notes="طلمبة هيدروليك"),
            BOMLine(equipment_id=frm.id, material_id=st37.id,  qty=Decimal("220"), unit_cost=Decimal("16"),    total_cost=Decimal("3520"),  notes="هيكل رئيسي 6mm"),
            BOMLine(equipment_id=frm.id, material_id=bolt.id,  qty=Decimal("120"), unit_cost=Decimal("8"),     total_cost=Decimal("960"),   notes="مسامير تثبيت"),
        ]
        db.add_all(bom)

        # ── 5. خلاط الأعلاف MX-200 ───────────────────────────────
        mx = Equipment(code="MX-200", name_ar="خلاط أعلاف أفقي 2 طن", name_en="Feed Mixer 2T MX-200", description="خلاط أعلاف سعة 2 طن/دفعة", level=0, weight_kg=Decimal("1600"), cad_drawing_no="DWG-MX200-Rev1")
        db.add(mx); await db.flush()

        mx_drm = Equipment(code="MX200-DRM", name_ar="اسطوانة الخلط",    name_en="Mixing Drum",  parent_id=mx.id, level=1, weight_kg=Decimal("800"))
        mx_drv = Equipment(code="MX200-DRV", name_ar="وحدة تشغيل الخلاط",name_en="Mixer Drive",  parent_id=mx.id, level=1, weight_kg=Decimal("350"))
        mx_frm = Equipment(code="MX200-FRM", name_ar="هيكل الخلاط",       name_en="Mixer Frame",  parent_id=mx.id, level=1, weight_kg=Decimal("450"))
        db.add_all([mx_drm,mx_drv,mx_frm]); await db.flush()

        bom_mx = [
            BOMLine(equipment_id=mx_drm.id, material_id=st52.id,  qty=Decimal("380"), unit_cost=Decimal("18.50"), total_cost=Decimal("7030")),
            BOMLine(equipment_id=mx_drm.id, material_id=pipe.id,  qty=Decimal("6"),   unit_cost=Decimal("85"),    total_cost=Decimal("510")),
            BOMLine(equipment_id=mx_drv.id, material_id=mot75.id, qty=Decimal("1"),   unit_cost=Decimal("4100"),  total_cost=Decimal("4100")),
            BOMLine(equipment_id=mx_drv.id, material_id=gbox.id,  qty=Decimal("1"),   unit_cost=Decimal("3800"),  total_cost=Decimal("3800")),
            BOMLine(equipment_id=mx_frm.id, material_id=st37.id,  qty=Decimal("260"), unit_cost=Decimal("16"),    total_cost=Decimal("4160")),
            BOMLine(equipment_id=mx_frm.id, material_id=weld.id,  qty=Decimal("10"),  unit_cost=Decimal("35"),    total_cost=Decimal("350")),
        ]
        db.add_all(bom_mx)

        # ── 6. العاملون ───────────────────────────────────────────
        workers = [
            Worker(code="W-001", name="أحمد محمد سالم",    job_title="رئيس ورشة",       phone="01001234567", daily_wage=Decimal("350"), base_weekly_wage=Decimal("2100"), hire_date=date(2020,3,1)),
            Worker(code="W-002", name="محمود علي حسن",     job_title="لحام درجة أولى",  phone="01112345678", daily_wage=Decimal("250"), base_weekly_wage=Decimal("1500"), hire_date=date(2021,6,15)),
            Worker(code="W-003", name="عمر خالد إبراهيم",  job_title="خراط",            phone="01223456789", daily_wage=Decimal("220"), base_weekly_wage=Decimal("1320"), hire_date=date(2022,1,10)),
            Worker(code="W-004", name="كريم سامي محمد",    job_title="كهربائي",         phone="01534567890", daily_wage=Decimal("200"), base_weekly_wage=Decimal("1200"), hire_date=date(2022,9,1)),
            Worker(code="W-005", name="طارق عبدالله رضا",   job_title="مساعد لحام",      phone="01645678901", daily_wage=Decimal("150"), base_weekly_wage=Decimal("900"),  hire_date=date(2023,3,20)),
            Worker(code="W-006", name="يوسف مصطفى صالح",   job_title="عامل إنتاج",      phone="01756789012", daily_wage=Decimal("130"), base_weekly_wage=Decimal("780"),  hire_date=date(2023,7,1)),
        ]
        db.add_all(workers)

        # ── 7. العملاء ────────────────────────────────────────────
        customers = [
            Customer(code="C-001", name="شركة الدلتا للدواجن",     phone="0223456789", address="المنصورة، الدقهلية", credit_limit=Decimal("500000"), balance=Decimal("-85000")),
            Customer(code="C-002", name="مزرعة النيل للأعلاف",     phone="0234567890", address="الجيزة",             credit_limit=Decimal("300000"), balance=Decimal("-45000")),
            Customer(code="C-003", name="مصنع الغذاء الحيواني",    phone="0245678901", address="بني سويف",           credit_limit=Decimal("750000"), balance=Decimal("0")),
            Customer(code="C-004", name="شركة الأندلس للزراعة",    phone="0256789012", address="الإسكندرية",         credit_limit=Decimal("200000"), balance=Decimal("-120000")),
        ]
        db.add_all(customers)
        await db.flush()

        # ── 8. أوامر الإنتاج وتكاليف ─────────────────────────────
        wo1 = WorkOrder(code="WO-2024-001", equipment_id=fg.id, status="in_progress",
            planned_cost=Decimal("185000"), actual_cost=Decimal("0"),
            start_date=date(2024,2,1), end_date=date(2024,4,15),
            notes="FG-500 لشركة الدلتا للدواجن")
        wo2 = WorkOrder(code="WO-2024-002", equipment_id=mx.id, status="draft",
            planned_cost=Decimal("95000"), actual_cost=Decimal("0"),
            start_date=date(2024,3,1), end_date=date(2024,4,30),
            notes="MX-200 لمزرعة النيل")
        db.add_all([wo1,wo2]); await db.flush()

        cls = [
            CostLine(work_order_id=wo1.id, cost_type="material", description="فولاذ هيكل وطحن", qty=Decimal("600"),  unit_cost=Decimal("18.50"), total_cost=Decimal("11100"), material_id=st52.id),
            CostLine(work_order_id=wo1.id, cost_type="material", description="موتور 15KW",       qty=Decimal("1"),    unit_cost=Decimal("7200"),  total_cost=Decimal("7200"),  material_id=mot15.id),
            CostLine(work_order_id=wo1.id, cost_type="material", description="انفرتر تحكم",      qty=Decimal("1"),    unit_cost=Decimal("5500"),  total_cost=Decimal("5500"),  material_id=inv.id),
            CostLine(work_order_id=wo1.id, cost_type="labor",    description="لحام وتصنيع",      qty=Decimal("80"),   unit_cost=Decimal("250"),   total_cost=Decimal("20000")),
            CostLine(work_order_id=wo1.id, cost_type="labor",    description="تجميع وضبط",       qty=Decimal("40"),   unit_cost=Decimal("200"),   total_cost=Decimal("8000")),
            CostLine(work_order_id=wo1.id, cost_type="overhead", description="كهرباء وغاز",      qty=Decimal("1"),    unit_cost=Decimal("6500"),  total_cost=Decimal("6500")),
        ]
        db.add_all(cls)
        wo1.actual_cost = sum(c.total_cost for c in cls)

        # طلبات العملاء
        orders = [
            CustomerOrder(code="ORD-2024-001", customer_id=customers[0].id, equipment_id=fg.id,
                description="مجرشة FG-500 مع تركيب", quantity=1,
                unit_price=Decimal("250000"), total_price=Decimal("250000"),
                status="in_progress", order_date=date(2024,1,20), delivery_date=date(2024,4,30)),
            CustomerOrder(code="ORD-2024-002", customer_id=customers[1].id, equipment_id=mx.id,
                description="خلاط أعلاف MX-200", quantity=1,
                unit_price=Decimal("130000"), total_price=Decimal("130000"),
                status="pending", order_date=date(2024,2,10), delivery_date=date(2024,5,15)),
            CustomerOrder(code="ORD-2024-003", customer_id=customers[3].id,
                description="قطع غيار شاشات غربلة", quantity=6,
                unit_price=Decimal("1500"), total_price=Decimal("9000"),
                status="delivered", order_date=date(2024,1,5), delivery_date=date(2024,1,20)),
        ]
        db.add_all(orders)
        await db.commit()

        print("✅ Seed complete — ورشة معدات الأعلاف")
        print(f"   Equipment root ID : {fg.id}")
        print(f"   معدات: FG-500 (مجرشة 5طن/ساعة) + MX-200 (خلاط 2طن)")
        print(f"   مواد: {len(mats)} صنف في 7 تصنيفات")
        print(f"   عاملون: {len(workers)}")
        print(f"   عملاء: {len(customers)}")
        print(f"   Work Order : WO-2024-001 — تكلفة فعلية: {wo1.actual_cost:,.2f} ج")


if __name__ == "__main__":
    asyncio.run(seed())

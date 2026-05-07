# Heavy Equipment Workshop ERP
## نظام ERP لورشة تصنيع المعدات الثقيلة

---

## هيكل المشروع

```
heavy-erp/
├── docker-compose.yml          ← تنسيق كل الخدمات
├── Makefile                    ← أوامر مختصرة
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seed.py                 ← بيانات تجريبية
│   ├── alembic.ini
│   ├── migrations/
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   └── app/
│       ├── main.py             ← FastAPI entry point
│       ├── core/
│       │   ├── config.py       ← الإعدادات
│       │   └── database.py     ← SQLAlchemy async engine
│       ├── models/
│       │   └── models.py       ← جداول قاعدة البيانات
│       ├── schemas/
│       │   └── schemas.py      ← Pydantic validation
│       ├── services/
│       │   ├── inventory.py    ← منطق المخازن
│       │   ├── equipment.py    ← منطق المعدات والBOM
│       │   └── accounting.py   ← منطق المحاسبة
│       └── api/
│           ├── inventory.py    ← REST endpoints المخازن
│           ├── equipment.py    ← REST endpoints المعدات
│           └── accounting.py   ← REST endpoints المحاسبة
├── frontend/
│   └── index.html              ← واجهة المستخدم (HTML+JS)
├── nginx/
│   └── nginx.conf              ← Reverse proxy
└── postgres/
    └── init.sql                ← إعداد أولي لقاعدة البيانات
```

---

## متطلبات التشغيل

- Docker Desktop (تنزيل من https://docker.com)
- لا تحتاج Python أو أي شيء آخر على جهازك

---

## خطوات التشغيل خطوة بخطوة

### الخطوة 1 — نسخ المشروع

```bash
# نزّل المشروع أو اضغط unzip على الملف
cd heavy-erp
```

### الخطوة 2 — تشغيل كل الخدمات

```bash
make up
# أو بدون make:
docker compose up -d
```

سيتم تلقائياً:
- تشغيل قاعدة بيانات PostgreSQL
- بناء صورة FastAPI
- تشغيل Redis
- تشغيل Nginx
- تنفيذ migrations (إنشاء الجداول)

### الخطوة 3 — إضافة البيانات التجريبية

```bash
make seed
# أو:
docker compose exec backend python seed.py
```

ستضاف:
- 5 تصنيفات مواد
- 8 مواد خام (فولاذ، هيدروليك، كهرباء...)
- معدة كاملة: حفار هيدروليكي HD-320
- هيكل شجري بـ 4 مستويات + BOM كامل
- أمر إنتاج مع سطور تكلفة

### الخطوة 4 — فتح النظام

| الرابط | الوصف |
|--------|-------|
| http://localhost | واجهة المستخدم |
| http://localhost/docs | Swagger API التفاعلية |
| http://localhost/api/v1 | API مباشرة |

---

## API Endpoints

### المخازن
```
GET    /api/v1/inventory/materials          ← قائمة المواد
POST   /api/v1/inventory/materials          ← إضافة مادة
GET    /api/v1/inventory/materials/{id}     ← تفاصيل مادة
POST   /api/v1/inventory/movements          ← تسجيل حركة
GET    /api/v1/inventory/movements/{mat_id} ← حركات مادة
GET    /api/v1/inventory/alerts/low-stock   ← تنبيهات النقص
```

### المعدات والBOM
```
GET    /api/v1/equipment                    ← قائمة المعدات
POST   /api/v1/equipment                    ← إضافة معدة
GET    /api/v1/equipment/{id}/tree          ← شجرة كاملة مع التكاليف
GET    /api/v1/equipment/{id}/bom           ← قائمة المواد
GET    /api/v1/equipment/{id}/bom/cost      ← تفكيك التكلفة
POST   /api/v1/equipment/bom               ← إضافة سطر BOM
POST   /api/v1/equipment/{id}/dimensions   ← إضافة مقاس
```

### المحاسبة
```
GET    /api/v1/accounting/dashboard         ← إحصائيات عامة
POST   /api/v1/accounting/work-orders       ← إنشاء أمر إنتاج
GET    /api/v1/accounting/work-orders       ← قائمة الأوامر
POST   /api/v1/accounting/cost-lines        ← إضافة تكلفة
GET    /api/v1/accounting/work-orders/{id}/variance ← انحراف التكلفة
```

---

## أوامر مفيدة

```bash
make logs          # متابعة logs الـ backend
make shell-backend # فتح bash داخل الـ container
make shell-db      # فتح psql للتعديل المباشر
make migrate       # تشغيل migrations
make rollback      # التراجع عن آخر migration
make test          # اختبار سريع للـ API
make clean         # مسح كل البيانات والبدء من جديد
make down          # إيقاف كل الخدمات
```

---

## مثال: إضافة معدة جديدة عبر API

```bash
# 1. إضافة معدة رئيسية
curl -X POST http://localhost/api/v1/equipment \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CRANE-100",
    "name_ar": "رافعة برجية 100 طن",
    "name_en": "Tower Crane 100T",
    "level": 0,
    "weight_kg": 45000,
    "cad_drawing_no": "DWG-CR100-ASSY-Rev1"
  }'

# 2. عرض شجرة المعدة مع التكاليف
curl http://localhost/api/v1/equipment/1/tree
```

---

## التقنيات المستخدمة

| التقنية | الغرض |
|---------|-------|
| FastAPI | REST API سريع مع async |
| SQLAlchemy 2 (async) | ORM لقاعدة البيانات |
| PostgreSQL 16 | قاعدة البيانات الرئيسية |
| Alembic | إدارة migrations |
| Pydantic v2 | التحقق من البيانات |
| Redis | Cache وقائمة المهام |
| Nginx | Reverse proxy وملفات ثابتة |
| Docker Compose | تنسيق الخدمات |
| Vanilla HTML/JS | واجهة المستخدم |

---

## الخطوات القادمة (الإصدار 2)

- [ ] JWT Authentication وصلاحيات المستخدمين
- [ ] رفع ملفات CAD (DWG/STEP) مباشرة
- [ ] تقارير PDF للـ BOM والتكاليف
- [ ] نظام المشتريات وطلبات الشراء
- [ ] لوحة تحكم بالرسوم البيانية (Chart.js)
- [ ] تطبيق موبايل للمخازن (barcode scanning)

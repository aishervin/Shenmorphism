# 📋 راهنمای تنظیمات Cloudflare KV

## مراحل راه‌اندازی سیستم مدیریت کلید API

### 1️⃣ ایجاد KV Namespace

1. وارد داشبورد Cloudflare شوید: [dash.cloudflare.com](https://dash.cloudflare.com)
2. از منوی سمت چپ به **Workers & Pages** → **KV** بروید
3. روی دکمه **Create a namespace** کلیک کنید
4. نام namespace را `shen_user_db` وارد کنید
5. روی **Add** کلیک کنید
6. ID namespace را کپی کنید (مثلاً: `abc123def456...`)

### 2️⃣ اتصال KV به پروژه Cloudflare Pages

1. به بخش **Workers & Pages** → **Pages** بروید
2. پروژه SHΞN™ Morphism خود را انتخاب کنید
3. به تب **Settings** → **Functions** بروید
4. در بخش **KV namespace bindings** روی **Add binding** کلیک کنید
5. اطلاعات زیر را وارد کنید:
   - **Variable name**: `shen_user_db`
   - **KV namespace**: `shen_user_db` (همان که ساختید)
6. روی **Save** کلیک کنید

### 3️⃣ دیپلوی مجدد

بعد از ذخیره binding، باید یک دیپلوی مجدد انجام دهید:

1. به تب **Deployments** بروید
2. روی **Retry deployment** برای آخرین deployment کلیک کنید
3. یا یک commit جدید به repository push کنید

### 4️⃣ تست سیستم

بعد از دیپلوی موفق:

1. سایت را باز کنید
2. روی دکمه ✏️ ویرایش کد یک کامپوننت کلیک کنید
3. باید پاپ‌آپ درخواست کلید API نمایش داده شود
4. کلید Gemini خود را وارد کرده و ذخیره کنید
5. کلید در KV ذخیره شده و برای مراجعات بعدی استفاده می‌شود

---

## 🔧 ساختار داده‌های ذخیره شده در KV

هر کاربر در KV با فرمت زیر ذخیره می‌شود:

```json
{
  "geminiKey": "AIzaSy...",
  "createdAt": 1720000000000,
  "usageCount": 5,
  "lastUsed": 1720000000000,
  "dailyLimit": 50,
  "lastReset": 1720000000000
}
```

### فیلدها:
- `geminiKey`: کلید API جمنای کاربر
- `createdAt`: زمان ثبت کلید (timestamp)
- `usageCount`: تعداد درخواست‌های استفاده شده امروز
- `lastUsed`: آخرین زمان استفاده
- `dailyLimit`: سهمیه روزانه (پیش‌فرض: 50)
- `lastReset`: زمان بازنشانی سهمیه روزانه

---

## 📊 API Endpoints

سیستم 3 endpoint اصلی دارد:

### 1. ثبت کلید API
```
POST /api/key-register
Body: { "userId": "user_abc123", "geminiKey": "AIzaSy..." }
Response: { "success": true, "message": "API key registered successfully" }
```

### 2. بررسی وضعیت کلید
```
GET /api/key-check?userId=user_abc123
Response: { 
  "exists": true, 
  "canUse": true, 
  "usageCount": 5, 
  "dailyLimit": 50, 
  "remaining": 45 
}
```

### 3. افزایش شمارنده استفاده
```
GET /api/usage?userId=user_abc123
Response: { 
  "success": true, 
  "usageCount": 6, 
  "dailyLimit": 50, 
  "remaining": 44 
}
```

---

## 🎯 نکات مهم

- ✅ کلیدهای API به صورت امن در KV ذخیره می‌شوند
- ✅ سهمیه روزانه هر 24 ساعت بازنشانی می‌شود
- ✅ شناسه کاربری به صورت خودکار تولید می‌شود
- ✅ پشتیبان‌گیری در localStorage نیز انجام می‌شود
- ✅ قابلیت ردیابی استفاده برای هر کاربر

---

## 🚀 عیب‌یابی

### مشکل: خطا در ثبت کلید
- مطمئن شوید KV namespace درست متصل شده
- بررسی کنید deployment موفق بوده باشد
- کنسول مرورگر را برای خطاهای JavaScript چک کنید

### مشکل: سهمیه بازنشانی نمی‌شود
- سیستم به صورت خودکار هر 24 ساعت سهمیه را بازنشانی می‌کند
- زمان آخرین بازنشانی در فیلد `lastReset` ذخیره می‌شود

### مشکل: کلید پیدا نمی‌شود
- بررسی کنید userId درست تولید شده باشد
- در داشبورد Cloudflare به بخش KV بروید و کلیدها را چک کنید

---

## 📞 پشتیبانی

برای مشکلات بیشتر، لاگ‌های Cloudflare Functions را بررسی کنید:
1. به **Workers & Pages** → **Your Project** → **Functions** → **Logs** بروید
2. لاگ‌های مربوط به `/api/*` را بررسی کنید

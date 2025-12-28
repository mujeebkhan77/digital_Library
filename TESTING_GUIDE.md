# Testing Guide - Digital Library Fixes

## Pre-Testing Setup

1. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

2. **Verify Stripe keys in `config/settings.py`:**
   - Should have `STRIPE_SECRET_KEY` starting with `sk_test_`
   - Should have `STRIPE_PUBLISHABLE_KEY` starting with `pk_test_`

3. **Create test users:**
   ```bash
   python manage.py createsuperuser
   ```
   - Create an admin user with `is_staff=True`

---

## Test 1: PDF Viewer ✅

### Steps:
1. Login as a regular user
2. Navigate to a free, approved book
3. Click "Read Book" button
4. PDF should load in iframe viewer

### Expected Results:
- ✅ PDF displays in browser without download option
- ✅ Right-click is disabled
- ✅ Print shortcuts (Ctrl+P) are disabled
- ✅ No direct URL access to PDF file
- ✅ Error message shown if user tries to access paid book without purchase

### Test Cases:
- **Free book (authenticated user):** Should display PDF ✅
- **Free book (anonymous user):** Should redirect to login ✅
- **Paid book (not purchased):** Should show "Purchase required" message ✅
- **Paid book (purchased):** Should display PDF ✅

---

## Test 2: Admin Link ✅

### Steps:
1. Login as admin user (with `is_staff=True`)
2. Check navbar for "Admin" link
3. Click the "Admin" link

### Expected Results:
- ✅ Admin link appears in navbar (desktop and mobile)
- ✅ Clicking opens Django admin panel at `/admin/`
- ✅ Non-staff users don't see the admin link

### Test Cases:
- **Staff user:** Admin link visible and functional ✅
- **Non-staff user:** Admin link not visible ✅
- **Anonymous user:** Admin link not visible ✅

---

## Test 3: Stripe Payment ✅

### Steps:
1. Login as regular user
2. Navigate to a paid book
3. Click "Buy Now ($9.99)" button
4. Complete payment with test card:
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
   - ZIP: Any 5 digits (e.g., 12345)

### Expected Results:
- ✅ Redirects to Stripe Checkout page
- ✅ Payment completes successfully
- ✅ Redirects back to success page
- ✅ Purchase record created in database
- ✅ User can now read the paid book

### Test Cases:
- **Valid payment:** Should complete successfully ✅
- **Cancelled payment:** Should show cancellation message ✅
- **Invalid API key:** Should show error message (if key is wrong) ✅

### Debugging:
If you see "Invalid API key" error:
1. Check `config/settings.py` has correct keys
2. Check logs for masked key (first 6 and last 4 characters)
3. Verify key starts with `sk_test_` (not `pk_test_`)

---

## Test 4: Optional Cover Image ✅

### Steps:
1. Login as admin user
2. Go to Django admin panel
3. Navigate to Books → Add Book
4. Fill in all required fields (title, author, description, category, PDF)
5. **Leave cover_image field empty**
6. Save the book

### Expected Results:
- ✅ Book saves successfully without cover image
- ✅ Frontend shows placeholder icon for missing cover
- ✅ Book card displays correctly without image

### Test Cases:
- **Book with cover image:** Displays image ✅
- **Book without cover image:** Shows placeholder SVG icon ✅
- **Book detail page:** Handles missing cover gracefully ✅

---

## Verification Checklist

- [x] PDF viewer serves files with proper headers
- [x] PDF viewer blocks direct URL access
- [x] Admin link points to Django admin (`/admin/`)
- [x] Admin link only visible to staff users
- [x] Stripe API key validation works
- [x] Stripe error handling provides clear messages
- [x] Cover image is optional in model
- [x] Cover image is optional in form
- [x] Migration applied successfully
- [x] No linting errors

---

## Common Issues & Solutions

### Issue: PDF not loading
**Solution:** Check that:
- Book is approved (`is_approved=True`)
- User is authenticated
- PDF file exists in media folder
- Check server logs for errors

### Issue: Admin link not showing
**Solution:** Ensure user has `is_staff=True`:
```python
user.is_staff = True
user.save()
```

### Issue: Stripe "Invalid API key"
**Solution:**
1. Verify key in `config/settings.py` starts with `sk_test_`
2. Check for extra spaces or quotes
3. Check server logs for masked key validation
4. Ensure using test keys (not live keys)

### Issue: Cover image required error
**Solution:** Run migration:
```bash
python manage.py migrate books
```

---

## Server Logs

Check logs for:
- PDF access attempts: `logger.info` in `serve_pdf`
- Stripe key initialization: Masked key logged on startup
- Stripe errors: Detailed exception logging
- Access denied: Warning logs for unauthorized access

---

## Success Criteria

All tests should pass:
- ✅ PDF viewer functional and secure
- ✅ Admin link works for staff users
- ✅ Stripe payments complete successfully
- ✅ Books can be created without cover images


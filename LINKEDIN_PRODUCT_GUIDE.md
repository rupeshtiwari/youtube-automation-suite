# LinkedIn Products Guide - Which One to Enable

## 🔍 Your Products Page Shows:

Looking at your Products page, I see:
- **Share on LinkedIn** - "Request access" button available
- **Pages Data Portability API** - "Review in progress"
- Many other products

## ✅ SOLUTION: Request "Share on LinkedIn"

The `w_member_social` scope (needed for posting) is typically provided by the **"Share on LinkedIn"** product.

### Step-by-Step:

1. **Find "Share on LinkedIn"** in your products list
   - It should be near the top
   - Description: "Amplify your content by sharing it on LinkedIn"

2. **Click "Request access"** button

3. **Fill out the Access Request Form**:
   - **Use case**: "I want to automatically post video content from YouTube to LinkedIn for business marketing"
   - **Description**: "This application automates the posting of educational video content from YouTube to LinkedIn to expand reach and engagement. The app will post content on behalf of the business owner to their LinkedIn profile."
   - **Accept terms** and submit

4. **Wait for approval** (can be instant or 1-3 business days)

5. **After approval**:
   - Go back to "Auth" tab
   - You should now see scopes available
   - The `w_member_social` scope should be available

## 📋 Why "Share on LinkedIn"?

- This product provides the `w_member_social` scope
- This scope is required for posting content to LinkedIn
- "Marketing Developer Platform" might not be available for your app type or has been replaced

## ⚠️ Important Notes:

- **"Share on LinkedIn"** is the product that provides posting capabilities
- Without it, `w_member_social` scope won't be available
- The approval process is required by LinkedIn

## 🚀 Next Steps:

1. Click "Request access" on **"Share on LinkedIn"**
2. Fill out the form with your use case
3. Wait for approval email
4. Test the OAuth flow again after approval


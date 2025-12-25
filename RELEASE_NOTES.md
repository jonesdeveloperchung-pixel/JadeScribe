# JadeScribe 1.1.0 Update

## New Features
*   **Multi-Item Detection:** The AI now scans for *all* pendants in a single image/tray.
*   **Marketing Suite:** Generates 3 distinct description styles:
    *   **Classical (Hero):** Poetic and refined.
    *   **Modern:** Direct, feature-focused for e-commerce.
    *   **Social:** Short, engaging text with emojis and hashtags.
*   **Web Preview:** Visualize how descriptions look on a mock product page.
*   **CSV Export:** One-click download of your entire inventory for Shopify/WooCommerce.

## Technical Changes
*   **Database:** `items` table now includes `description_modern` and `description_social`.
*   **Migration:** Automatic DB migration on startup.
*   **AI Models:** Prompts updated for JSON Array output and multi-style generation.

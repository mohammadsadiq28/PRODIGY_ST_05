PRODIGY_ST_05 – Automated Checkout Flow Testing
✅ Task Overview

For this task, I worked on building an automated test script that mimics a real user’s shopping journey on an e-commerce site. The idea was to go through the complete flow — add a product to the cart, checkout, and confirm the purchase — all handled by Python + Selenium + Pytest.

🔧 Tools & Tech

Python for scripting

Selenium for browser automation

Pytest for running and organizing tests

Chrome as the main browser

🛑 What I Found Initially

I started with Automation Practice
, but while testing I noticed a critical bug: every product on the homepage was marked “Out of Stock”. Since the Add to Cart button was disabled, it was impossible to test the checkout process.

🔄 Switching to a Reliable Site

To keep moving forward, I shifted to SauceDemo
 — a demo site built for automation practice.

🧪 Test Flow Covered

Here’s what my script does step by step:

Login → logs in with valid user credentials.

Add to Cart → selects “Sauce Labs Backpack” and adds it to the cart.

Cart Check → confirms the item is listed in the cart.

Checkout Info → fills in details like first name, last name, and postal code.

Finish Order → completes the checkout process.

Success Check → makes sure the confirmation message “Thank you for your order!” is displayed.

💻 Final Note

The full working script is in this repo. This task was not just about writing automation but also about finding bugs, reporting them, and adapting the testing strategy when the original site didn’t allow purchases.

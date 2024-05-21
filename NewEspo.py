import asyncio
from playwright.async_api import async_playwright
import os

async def login_and_export_contacts():
    username = 'speedy'
    password = 'Speedy#123'
    login_url = 'https://crm.highendrefrigeratorrepair.com/#'
    contacts_url = 'https://crm.highendrefrigeratorrepair.com/#Contact'
    # Define the download path as the default Downloads directory on macOS
    download_path = os.path.expanduser('~/Downloads')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, accept_downloads=True)  # Set headless=True if you don't want to open the browser window
        page = await browser.new_page()

        # Set the download path
        await page.context.set_default_downloads_path(download_path)

        await page.goto(login_url)

        # Wait for the login page to load
        await page.wait_for_selector('input[name="username"]')

        # Fill in the username and password fields
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)

        # Click the login button
        await page.click('button[type="submit"]')

        # Wait for the navigation after login
        await page.wait_for_load_state('networkidle')

        # Navigate to the contacts page
        await page.goto(contacts_url)

        # Optionally wait for the contacts page to load
        await page.wait_for_load_state('networkidle')

        # Scroll down and click "Show more" until all records are shown
        while True:
            try:
                # Click the "Show more" button if it's visible
                await page.click('text=Show more')
                await page.wait_for_timeout(1000)  # Wait for the new records to load
            except Exception as e:
                # Break the loop if the "Show more" button is not found
                print("No more records to load or an error occurred:", e)
                break

        # Select all records by clicking the top checkbox with class "select-all"
        await page.click('input.select-all')

        # Click the "Actions" button using the correct selector
        await page.click('button.actions-button')

        # Click the "Export" option using the correct selector
        await page.click('a.mass-action[data-action="export"]')

        # Click the final "Export" button in the pop-up to download the XLSX file
        await page.wait_for_selector('button[type="button"]:has-text("Export")')
        async with page.expect_download() as download_info:
            await page.click('button[type="button"]:has-text("Export")')
        download = await download_info.value
        await download.save_as(os.path.join(download_path, download.suggested_filename))

        # Keep the browser open for a while to complete the download
        await asyncio.sleep(30)

        # Close the browser
        await browser.close()

asyncio.run(login_and_export_contacts())

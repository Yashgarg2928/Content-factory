import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import shutil
import tempfile
import imapclient
import email
from email.header import decode_header
import re

# --- Helper Functions ---

def print_with_time(message):
    """Prints a message with a timestamp."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - {message}")

def create_temporary_chrome_profile():
    """Creates a temporary Chrome profile directory."""
    temp_profile_dir = tempfile.mkdtemp()
    print_with_time(f"Created temporary profile directory: {temp_profile_dir}")
    return temp_profile_dir

def setup_chrome_driver_temporary_profile(temp_profile_dir):
    """Sets up the Chrome WebDriver with a temporary profile."""
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={temp_profile_dir}")  # Use the temporary directory
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1366, 768)  # Adjust as needed
    return driver

def delete_temporary_chrome_profile(temp_profile_dir):
    """Deletes the temporary Chrome profile directory."""
    try:
        shutil.rmtree(temp_profile_dir)
        print_with_time(f"Deleted temporary profile directory: {temp_profile_dir}")
    except Exception as e:
        print_with_time(f"Error deleting temporary profile directory: {str(e)}")

def find_element(driver, by, selector, timeout=30):
    """Finds an element using WebDriverWait with specified timeout."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))  # Wait for clickable
        )
        return element
    except TimeoutException:
        print_with_time(f"Timeout: Element not found - {by}: {selector}")
        return None
    except NoSuchElementException:
        print_with_time(f"Element not found - {by}: {selector}")
        return None

def click_element(driver, element, use_js=False):
    """Clicks an element, handling potential exceptions."""
    try:
        if use_js:
            driver.execute_script("arguments[0].click();", element)
        else:
            element.click()
        return True
    except ElementClickInterceptedException as e:
        print_with_time(f"ElementClickInterceptedException: {str(e)}")
        return False
    except Exception as e:
        print_with_time(f"Error clicking element: {str(e)}")
        return False

def enter_text(driver, element, text):
    """Enters text into an element, handling potential issues."""
    try:
        element.clear()
        element.click()  # Ensure focus
        element.send_keys(text)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", element)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { 'bubbles': true }));", element)
        return True
    except Exception as e:
        print_with_time(f"Error entering text: {str(e)}")
        return False

def get_verification_code_from_email(email_address, password):
    """Retrieves the verification code from the subject of the latest email from Piclumen."""
    try:
        print_with_time("Attempting to retrieve verification code from email subject...")

        # Connect to Gmail's IMAP server
        imap_obj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
        print_with_time("Connecting to IMAP server...")
        imap_obj.login(email_address, password)
        print_with_time("Login successful...")

        # Select the inbox
        imap_obj.select_folder('INBOX')
        print_with_time("Inbox selected...")

        # Search for emails from Piclumen
        search_criteria = ['FROM', 'service@piclumen.com', 'SUBJECT', 'Your verification code is:']
        print_with_time(f"Searching for emails with criteria: {search_criteria}")
        UIDs = imap_obj.search(search_criteria)

        if not UIDs:
            print_with_time("No verification email found from Piclumen.")
            imap_obj.logout()
            return None

        # Get the most recent email
        latest_email_UID = UIDs[-1]
        print_with_time(f"Latest email UID: {latest_email_UID}")

        # Fetch the email subject
        print_with_time("Fetching email subject...")
        raw_messages = imap_obj.fetch([latest_email_UID], ['ENVELOPE']) # Only fetch the envelope

        #Get the envelope:
        envelope = raw_messages[latest_email_UID][b'ENVELOPE']

        #Get the subject:
        subject = envelope.subject.decode()

        print_with_time(f"Email subject: {subject}")

        # Extract the verification code (assuming it's a 4-digit number)
        match = re.search(r'(\d{4})', subject)  # find a 4 digit code
        if match:
            verification_code = match.group(1)
            print_with_time(f"Verification code found in subject: {verification_code}")
            imap_obj.logout()
            return verification_code
        else:
            print_with_time("Verification code not found in the email subject.")
            imap_obj.logout()
            return None

    except Exception as e:
        print_with_time(f"Error retrieving email: {str(e)}")
        return None

def first_sign_up(driver, email, password):
    """Enters email and password, clicks checkbox and submits the initial sign up form."""
    try:
        # Email Input
        email_input_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.form-item.pb-7.relative.w-full.mt-2 > div > div > div.n-input-wrapper > div > input"
        email_input = find_element(driver, By.CSS_SELECTOR, email_input_css)
        if email_input:
            if enter_text(driver, email_input, email):
                print_with_time("Email entered successfully.")
            else:
                print_with_time("Failed to enter email.")
                return False
        else:
            print_with_time("Email input not found.")
            return False

        # Password Input
        password_input_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div:nth-child(2) > div > div > div.n-input-wrapper > div > input"
        password_input = find_element(driver, By.CSS_SELECTOR, password_input_css)
        if password_input:
            if enter_text(driver, password_input, password):
                print_with_time("Password entered successfully.")
            else:
                print_with_time("Failed to enter password.")
                return False
        else:
            print_with_time("Password input not found.")
            return False

        # Checkbox
        checkbox_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.text-xs.flex.items-start.gap-2.break-all.w-full.cursor-pointer > span.custom-checkbox"
        checkbox = find_element(driver, By.CSS_SELECTOR, checkbox_css)
        if checkbox:
            driver.execute_script("arguments[0].click();", checkbox)
            print_with_time("Checkbox clicked successfully.")
        else:
            print_with_time("Checkbox not found.")
            return False

        # Submit Button
        first_submit_button_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.mt-8.w-full > button > span > span"
        first_submit_button = find_element(driver, By.CSS_SELECTOR, first_submit_button_css)
        if first_submit_button:
            driver.execute_script("arguments[0].click();", first_submit_button)
            print_with_time("First Submit button clicked successfully.")
        else:
            print_with_time("First Submit button not found.")
            return False

        return True

    except Exception as e:
        print_with_time(f"Error during initial sign up: {str(e)}")
        return False

def sign_up(driver, verification_code):
    """Enters the verification code and completes the sign-up process."""
    try:
        # Verification Code Input
        verification_code_input_xpath = "//*[@id=\"app\"]/div/div[1]/div[2]/div[1]/div/div[3]/div/div[1]/div[2]/div/div/div[1]/div/input"
        verification_code_input = find_element(driver, By.XPATH, verification_code_input_xpath)
        if verification_code_input:
            if enter_text(driver, verification_code_input, verification_code):
                print_with_time("Verification code entered successfully.")
            else:
                print_with_time("Failed to enter verification code.")
                return False
        else:
            print_with_time("Verification code input not found.")
            return False

        # Submit Button
        second_submit_button_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.mt-8.w-full > button > span > span"  # Replace with the actual CSS
        submit_button = find_element(driver, By.CSS_SELECTOR, second_submit_button_css)
        if submit_button:
            driver.execute_script("arguments[0].click();", submit_button)
            print_with_time("Final Submit button clicked successfully.")
        else:
            print_with_time("Final Submit button not found.")
            return False

        

        #Claim button
        claim_button_css = "body > div.n-modal-container > div > div > div.n-scrollbar-container > div > div.n-modal.relative.w-\[500px\].border.border-solid.border-border-1.flex.flex-col.rounded-2xl.overflow-hidden.bg-bg-3 > div.flex.justify-center.py-6.gap-x-3 > button.n-button.n-button--default-type.n-button--medium-type.min-w-\[120px\].h-10.px-3.\!bg-primary-6.\!text-text-white.hover\:\!bg-primary-5.active\:\!bg-primary-7"
        claim_button = find_element(driver, By.CSS_SELECTOR, claim_button_css)
        if claim_button:
            if click_element(driver, claim_button, use_js=True):
                print_with_time("claim button clicked successfully.")
            else:
                print_with_time("Failed to click claim button.")
                
        else:
            print_with_time("claim button not found.")

        return True

    except Exception as e:
        print_with_time(f"Error during sign up: {str(e)}")
        return False


def automate_piclumen_signup(email,gmail_password, password ):
    """Automates the Piclumen sign-up process."""

    temp_profile_dir = create_temporary_chrome_profile() # Create temp profile in function
    try:
        driver = setup_chrome_driver_temporary_profile(temp_profile_dir)
        driver.get("https://piclumen.com/app/account")

        # Find the "Sign up" button on login page
        sign_up_button_xpath = '''//*[@id="app"]/div/div[1]/div[2]/div[1]/div/div[3]/div/div[5]/span[2]'''
        sign_up_button = find_element(driver, By.XPATH, sign_up_button_xpath)

        if sign_up_button:
            print_with_time("Sign up button on login page found, attempting to click")
            if click_element(driver, sign_up_button, use_js=True):
                print_with_time("Clicked the Sign up button on the login page successfully")
                time.sleep(2)  # Wait for sign-up form to load

                 # Perform first sign up
                if first_sign_up(driver, email, password):
                  print_with_time("First sign up complete, submitting initial form")
                else:
                  print_with_time("First sign up incomplete, could not submit initial form")
                  return

                 # Wait for the verification code email to arrive - longer wait
                print_with_time("Waiting 10 seconds for email to arrive...")
                time.sleep(15)

                # Get the verification code from email
                verification_code = get_verification_code_from_email(email, gmail_password)

                if verification_code:
                  # Perform sign-up again (to enter the verification code)
                  if sign_up(driver, verification_code):
                      print_with_time("Sign up process completed successfully!")

                  else:
                      print_with_time("Sign up process failed during the final step.")

                else:
                   print_with_time("Failed to retrieve verification code. Sign up process aborted.")

            else:
                print_with_time("Failed to click the Sign up button on login page")
                return  # Stop if sign up button click fails
        else:
            print_with_time("Sign up button on login page not found")
            return  # Stop if sign up button not found

    except Exception as e:
      print_with_time(f"An error occurred during the automation process: {str(e)}")

    finally:
      try:
        driver.quit()
        delete_temporary_chrome_profile(temp_profile_dir)
      except Exception as e:
        print_with_time(f"Browser Closed with error: {str(e)}")

# --- Main Execution ---

if __name__ == "__main__":
    print_with_time("Starting Piclumen Sign-up Automation...")
    print_with_time('''To **enable IMAP** for your Gmail account, follow these steps:

---

### ✅ Step-by-Step Guide to Enable IMAP in Gmail:

1. **Log in to Gmail**
   Go to [https://mail.google.com](https://mail.google.com) and log into the Gmail account you want to use.

2. **Open Settings**

   * Click the **gear icon** in the top-right corner.
   * Click **“See all settings.”**

3. **Go to the "Forwarding and POP/IMAP" tab**

   * You’ll see it near the top right of the settings menu.

4. **Enable IMAP**

   * Scroll down to the **“IMAP access”** section.
   * Select **“Enable IMAP”**.
   * Click **“Save Changes”** at the bottom.

''')
    print_with_time('''To **enable 2-Step Verification** (also called 2-Factor Authentication or 2FA) on your **Gmail (Google) account**, follow this simple process:

---

### ✅ How to Enable 2-Step Verification for Gmail

#### 1. **Go to your Google Account security settings**

👉 [https://myaccount.google.com/security](https://myaccount.google.com/security)

#### 2. **Scroll down to "Signing in to Google"**

You will see a section like this:

* Password
* **2-Step Verification**
* App passwords (appears only after 2FA is enabled)

#### 3. **Click on "2-Step Verification"**

* Then click **“Get Started”**
* Log in again to confirm it’s you

#### 4. **Set up your second step** (Choose one):

* **Phone prompt** (recommended): Google will send a notification to your phone
* **Text message or call**: Receive a code via SMS or voice
* **Authenticator app** (Google Authenticator, Authy, etc.)
* **Backup codes** as fallback

#### 5. **Finish Setup**

* Complete the verification step
* Click **“Turn On”** to activate 2-Step Verification

---

### 🔐 Next Step: Create App Password (for your script)

After enabling 2FA, go to:
👉 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

* Select **Mail** as the app
* Select **Other (Custom name)**, and name it like `AutomationScript`
* It will generate a 16-character password — copy and use it in your Python script (instead of your Gmail password)

''')

    main_email = input("Enter Email id :")
    gmail_password = input("Enter Gmail pass: ")
    password = "Hello_word"
    quantity = int(input("ENTER NEEDED NUMBER OF ACCOUNT ---->"))
    
    with open("number.txt", "r") as file:
        start_no = int(file.read())
        print("resuming from  :--" , start_no)
    print("Total number of account after this :---- ", quantity + start_no )

    for i in range(start_no + 1, quantity + start_no):
        email = main_email[:-10] + f"+{i}" + main_email[-10:]
        print("ACCOUNT  -------> ", email)
        automate_piclumen_signup(email, gmail_password, password)
        with open("number.txt", "w") as file:
            file.write(f"{i}")
            

    print_with_time("Piclumen Sign-up Automation Complete.")
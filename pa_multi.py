import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import shutil
import tempfile
from email.header import decode_header
import logging
import requests
from concurrent.futures import ProcessPoolExecutor
import re
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper Functions

def find_element(driver, by, selector, timeout=10):
    """Find an element with a retry mechanism."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        logging.warning(f"Element with selector {selector} not found after {timeout} seconds.")
        return None

def click_element(driver, element, use_js=False):
    """Click an element with optional JavaScript execution."""
    try:
        if use_js:
            driver.execute_script("arguments[0].click();", element)
        else:
            element.click()
        return True
    except Exception as e:
        logging.error(f"Failed to click element: {e}")
        return False

def enter_text(driver, element, text):
    """Enter text into an element."""
    try:
        element.clear()
        element.send_keys(text)
        return True
    except Exception as e:
        logging.error(f"Failed to enter text: {e}")
        return False

def navigate_and_interact(driver):
    """Sets the image generation settings on Piclumen (e.g., aspect ratio, resolution)."""
    try:
        #no thanku button
        no_thanku_css = "#driver-popover-content > footer > span.driver-popover-navigation-btns > button.driver-popover-prev-btn"
        no_thanku_button = find_element(driver, By.CSS_SELECTOR, no_thanku_css)
        if no_thanku_button:
            if click_element(driver, no_thanku_button, use_js=True):
                logging.info("No thanku button clicked successfully.")
                time.sleep(5)  # Wait for page to load after signing in
            else:
                logging.warning("Failed to click no thanku button.")
                
        else:
            logging.info("no thanku button not found.")
            
        
        # Wait for the first button to be clickable and click it
        first_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '''//*[@id="genConfRef"]/div[1]/div[3]/div'''))
        )
        first_button.click()
        logging.info("Clicked the first button")
        

        # Wait for the popup and click the 9:16 button
        aspect_ratio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '9:16')]"))
        )
        aspect_ratio_button.click()
        logging.info("Clicked the 9:16 button")
   
        
        
        
        # Wait for the popup and click the third button with text "2"
        #third_button = WebDriverWait(driver, 10).until(
        #EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'switch-item')]/span[text()='2']"))
        #)
        #third_button.click()
        #logging.info("Clicked the third button with text '2'")
        return True
        # Continue with the prompts
        # ...

    except Exception as e:
        logging.error(f"Error: {e}")
        return False
        # print("Re-navigating to the URL")


def piclumen_sign_in(email, password, driver):
    """
    Opens a temporary Chrome instance, navigates to Piclumen,
    enters the email and password, and clicks the Sign In button.
    """

    try:
        driver.get("https://piclumen.com/app/account")
        time.sleep(2) # Wait for load
        # Email Input
        email_input_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.form-item.relative.pb-7.w-full.mt-2 > div > div > div.n-input-wrapper > div > input"
        email_input = find_element(driver, By.CSS_SELECTOR, email_input_css)
        if email_input:
            if enter_text(driver, email_input, email):
                logging.info("Email entered successfully.")
            else:
                logging.warning("Failed to enter email.")
                return False
        else:
            logging.warning("Email input not found.")
            return False

        # Password Input
        password_input_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div:nth-child(2) > div > div > div.n-input-wrapper > div > input"
        password_input = find_element(driver, By.CSS_SELECTOR, password_input_css)
        if password_input:
            if enter_text(driver, password_input, password):  # Replace "password" with actual password
                logging.info("Password entered successfully.")
            else:
                logging.warning("Failed to enter password.")
                return False
        else:
            logging.warning("Password input not found.")
            return False

        # Sign In Button
        sign_in_button_css = "#app > div > div.content.overflow-x-hidden.dark > div.absolute.pb-16.top-0.left-0.w-screen.min-h-full.h-max.flex.justify-center.items-center.text-dark-active-text > div.w-full.md\:w-\[488px\].relative.z-10.bg-black\/50.opacity-90.backdrop-blur-3xl.mb-24.md\:mb-0.md\:rounded-3xl.overflow-hidden > div > div.w-80.mx-auto.sign-in-account > div > div.mt-8.w-full > button > span > span"
        sign_in_button = find_element(driver, By.CSS_SELECTOR, sign_in_button_css)
        if sign_in_button:
            if click_element(driver, sign_in_button, use_js=True):
                logging.info("Sign In button clicked successfully.")
                time.sleep(5)  # Wait for page to load after signing in
            else:
                logging.warning("Failed to click Sign In button.")
                return False
        else:
            logging.warning("Sign In button not found.")
            return False

        #Claim button
        claim_button_css = "body > div.n-modal-container > div > div > div.n-scrollbar-container > div > div.n-modal.relative.w-\[500px\].border.border-solid.border-border-1.flex.flex-col.rounded-2xl.overflow-hidden.bg-bg-3 > div.flex.justify-center.py-6.gap-x-3 > button.n-button.n-button--default-type.n-button--medium-type.min-w-\[120px\].h-10.px-3.\!bg-primary-6.\!text-text-white.hover\:\!bg-primary-5.active\:\!bg-primary-7"
        claim_button = find_element(driver, By.CSS_SELECTOR, claim_button_css)
        if claim_button:
            if click_element(driver, claim_button, use_js=True):
                logging.info("claim button clicked successfully.")
                time.sleep(5)  # Wait for page to load after signing in
            else:
                logging.warning("Failed to click claim button.")
                
        else:
            logging.info("claim button not found.")
            
        

    

        return True  # Sign-in process completed successfully    
    except Exception as e:
        logging.error(f"An error occurred during sign-in: {str(e)}")
        return False

def download_image(driver, prompt, image_dir, image_number=0):
    """Downloads the generated image from PicLumen using Selenium."""
    try:
        # 1. Find the Container
        container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '''//*[@id="app"]/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div[1]/div'''))
        )

        # 2. Find Image
        img_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '''//*[@id="app"]/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div[1]/div/img'''))
        )
        # Scroll to the element before extracting info
        driver.execute_script("arguments[0].scrollIntoView();", img_element)

        if (container == None):
            logging.warning("Not able to find containers, probably not loaded page, quitting");
            return False

        # 3. Get image_url
        image_url = img_element.get_attribute('src')
        if not image_url:
            logging.warning("Image source URL not found. Aborting download.")
            return False

        logging.info(f"Image URL found: {image_url}")

        # 4. Construct the image name and the storage folder
        first_word = re.sub(r'[^a-zA-Z0-9]', '', prompt.split()[0])  # Use the first word of the prompt
        
        os.makedirs(image_dir, exist_ok=True)  # ensure images directory exists
        image_name = f"{first_word}{image_number}.jpg" if image_number > 0 else f"{first_word}.jpg"
        image_path = os.path.join(image_dir, image_name)

        # 5.  Download the image from the image url.
        logging.info(f"Downloading from {image_url} to {image_path}")
        response = requests.get(image_url, stream=False) #Switch stream to False
        response.raise_for_status()  # Raise an exception for bad status codes
        logging.info("got the image now saving it in pc")

        #with open(image_path, 'wb') as out_file:
         #   shutil.copyfileobj(response.raw, out_file)
        with open(image_path, 'wb') as f:
            f.write(response.content)

        logging.info(f"Downloaded image to {image_path}")
        
        return True

    except TimeoutException:
        logging.warning("Timeout occurred while waiting for image element.")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
        return False
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}") #Get full exceptions log
        return False



# Main Automation Function
def automate_piclumen(prompt_file_path, base_email, password, image_dir,start_id, images_per_email=10):
    """
    Automates image generation on Piclumen with temporary profiles and email cycling.

    Args:
        prompt_file_path (str): Path to the text file containing prompts.
        base_email (str): The base email address (e.g., "t63120403+").
        password (str): The password for the Piclumen account.
        images_per_email (int): Number of images that can be generated per email.
        start_id (int): The mail id from which user wants to start
    """

    # Added for pop up, not used for now but can be used to find element
    def is_generation_in_progress(driver, generation_in_progress_selectors):
        for selector in generation_in_progress_selectors:
            try:
                elements = driver.find_elements(By.XPATH if selector.startswith("//") else By.CSS_SELECTOR, selector)
                if elements:
                    return True
            except Exception:
                continue
        return False


    # Selectors for detecting generation in progress.
    generation_in_progress_selectors = [
        "//div[contains(text(), 'Generating')]",
        "//div[contains(@class, 'progress')]",
        "//span[contains(text(), 'Generating')]",
        "//div[contains(@class, 'loading')]",
        "//div[contains(@class, 'spinner')]",
        "//div[contains(@class, 'n-spin')]",
        "//div[contains(text(), 'Queued')]",
        "//span[contains(text(), 'Queued')]",
    ]

    # Load Prompts
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            prompts = [line.strip() for line in file if line.strip()]
            prompts = [prompt for line in prompts for prompt in (line,line,line,line)]

        if not prompts:
            logging.warning("No prompts found in the file.")
            return
    except FileNotFoundError:
        logging.error(f"Prompt file not found at {prompt_file_path}")
        return
    except Exception as e:
        logging.error(f"Error reading prompts: {e}")
        return


    # Email Management
    email_counter = start_id #Now it begins from the email id user is entering
    prompt_index = 0
    image_count = 0

    # Common input and Button selectors (outside the loop for efficiency)
    input_selectors = [
        "textarea.n-input__textarea-el",
        "//textarea[contains(@class, 'n-input__textarea-el')]",
        "//textarea",
        "textarea",
        "//div[contains(@class, 'textarea')]//textarea",
        "//div[contains(@class, 'input')]//textarea"
    ]

    button_selectors = [
        "button.n-button--primary-type",
        "//button[contains(@class, 'n-button--primary-type')]",
        "//button[contains(text(), 'Generate')]",
        "//button[contains(@class, 'primary')]",
        "//button[contains(@class, 'generate')]"
    ]


    while prompt_index < len(prompts):
        setup_condition = False
        while not setup_condition:

            # Create a temporary Chrome profile
            temp_profile_dir = tempfile.mkdtemp()
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f"user-data-dir={temp_profile_dir}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--headless=new")

            # Initialize the driver
            service = Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(1366, 768)  # Adjust as needed

            # Sign In
            current_email = f"{base_email}+{email_counter}@gmail.com"
            logging.info(f"Signing in with email: {current_email}")
            if not piclumen_sign_in(current_email, password, driver):
                logging.info(f"Failed to sign in with {current_email}. Exiting.")
                driver.quit() # Close Driver
                shutil.rmtree(temp_profile_dir, ignore_errors=True) # Clean Profile
                continue # Stop Processing


            # Setup Image Generation Settings
            driver.get("https://piclumen.com/app/image-generator/create")
            time.sleep(1.5)
            if not navigate_and_interact(driver): # Implement the navigation_and_interact code to do the settings
                logging.error("Failed to set up image generation settings. Exiting.")
                driver.quit() # Close Driver
                shutil.rmtree(temp_profile_dir, ignore_errors=True) # Clean Profile
                continue # Stop Processing

            setup_condition = True

        #Add more checking before continue
        # try:
        #      logging.info("Attempting to see the https://piclumen.com/app/account data ")
        #      image_url = driver.current_url;
        #      logging.info(image_url)
        # except Exception as e:
        #     logging.error(f"❌ Error during exception {e}")
        #     break # Break this inner loop and move to new chrome instance

        # Process Prompts with Image Limit
        local_image_count = 0 # Keep tracks of images in the loop, it ensures that two prompts are run
        while local_image_count < images_per_email and prompt_index < len(prompts):
            prompt = prompts[prompt_index]
            logging.info(f"Processing prompt: {prompt} (Image {local_image_count+1}/{images_per_email})")

            try:
                # Wait for the page to load
                wait = WebDriverWait(driver, 30)

                # Find the input field - try all selectors
                prompt_input = None
                for selector in input_selectors:
                    try:
                        if selector.startswith("//"):
                            prompt_input = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            prompt_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        logging.info(f"  Found input field using selector: {selector}")
                        break
                    except Exception:
                        continue

                if not prompt_input:
                    logging.warning("❌ Could not find the input field after trying all selectors.")
                    logging.warning("  Please check if the website layout has changed.")
                    break

                # Clear and input the prompt using a more robust method
                try:
                    # First clear the field
                    prompt_input.clear()
                    logging.info("  Cleared input field")

                    # Click to ensure focus
                    prompt_input.click()
                    logging.info("  Clicked input field to focus")

                    prompt_input.send_keys(prompt)

                    logging.info("  Successfully entered prompt text")

                    # Ensure the field changes are registered
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", prompt_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { 'bubbles': true }));", prompt_input)
                    logging.info("  Triggered input events")

                except Exception as e:
                    logging.warning(f"  Error setting prompt text: {str(e)}")
                    # Try alternative method - direct JavaScript + keyboard shortcuts
                    try:
                        logging.info("  Trying alternative input method...")
                        # Clear using keyboard shortcut
                        ActionChains(driver).click(prompt_input).perform()
                        ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        ActionChains(driver).send_keys(Keys.DELETE).perform()

                        # Type the text
                        ActionChains(driver).send_keys(prompt).perform()
                        logging.info("  Used ActionChains to input text")
                    except Exception as alt_e:
                        logging.warning(f"  Alternative input method also failed: {str(alt_e)}")
                        break

                # Find the generate button - try all selectors
                button_to_click = None
                for selector in button_selectors:
                    try:
                        if selector.startswith("//"):
                            button_to_click = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            button_to_click = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        logging.info(f"  Found button using selector: {selector}")
                        break
                    except Exception:
                        continue

                if not button_to_click:
                    logging.warning("❌ Could not find the generate button after trying all selectors.")
                    logging.warning("  Please check if the website layout has changed.")
                    break

                # Check if button is actually enabled
                is_enabled = True
                try:
                    # Try to check button state
                    is_enabled = button_to_click.is_enabled()
                    if not is_enabled:
                        logging.warning("⚠️ Generate button appears to be disabled.")
                        button_classes = button_to_click.get_attribute("class")
                        logging.info(f"  Button classes: {button_classes}")
                        if "disabled" in button_classes or "n-button--disabled" in button_classes:
                            logging.info("  Button is disabled. Waiting before trying again...")
                            break
                except Exception as e:
                    logging.warning(f"  Warning: Could not check button state: {str(e)}")

                # Try different ways to click the button
                click_successful = False
                try:
                    # First, try JavaScript click
                    logging.info("  Attempting to click button via JavaScript...")
                    driver.execute_script("arguments[0].click();", button_to_click)
                    logging.info("  JavaScript click completed")
                    click_successful = True
                except Exception as e:
                    logging.warning(f"  JavaScript click failed: {str(e)}")

                if not click_successful:
                    try:
                        # Then try Selenium click
                        logging.info("  Attempting to click button via Selenium...")
                        button_to_click.click()
                        logging.info("  Selenium click completed")
                        click_successful = True
                    except Exception as inner_e:
                        logging.warning(f"  Selenium click failed: {str(inner_e)}")

                if not click_successful:
                    try:
                        # Try ActionChains click as last resort
                        logging.info("  Attempting to click button via ActionChains...")
                        ActionChains(driver).move_to_element(button_to_click).click().perform()
                        logging.info("  ActionChains click completed")
                        click_successful = True
                    except Exception as ac_e:
                        logging.warning(f"  ActionChains click failed: {str(ac_e)}")

                if not click_successful:
                    logging.warning("  All click methods failed.")
                    break
                time.sleep(5)

                # Verify if generation has actually started
                generation_started = False
                start_time = time.time()
                max_check_time = 30  # Check for up to 30 seconds to see if generation started

                logging.info("  Checking if generation has started...")

                while not generation_started and (time.time() - start_time) < max_check_time:
                    # Look for indicators that generation has started
                    generation_started = is_generation_in_progress(driver,generation_in_progress_selectors)

                    if generation_started:
                        logging.info("  ✓ Generation confirmed to have started")
                        break

                    logging.info("  Waiting for generation to start...")
                    time.sleep(3)  # Check every 3 seconds

                if not generation_started:
                    logging.warning("⚠️ Could not confirm generation has started after 30 seconds.")
                    break

                # Wait for generation to complete with periodic status checks
                logging.info("  Waiting for generation to complete...")
                generation_start_time = time.time()

                while is_generation_in_progress(driver,generation_in_progress_selectors):
                    current_time = time.time()
                    elapsed_time = current_time - generation_start_time

                    # Check if we've exceeded maximum wait time
                    #No max wait time
                    time.sleep(10)  # Check status every few seconds
                # Generation appears to be complete
                generation_end_time = time.time()
                total_generation_time = generation_end_time - generation_start_time
                logging.info(f"  ✓ Generation complete! Took {total_generation_time:.1f} seconds")

                # Download Image with Number Suffix
                remainders = {
                    1: ((prompt_index +1) - 1) % 4,
                    2: ((prompt_index +1) - 2) % 4,
                    3: ((prompt_index +1) - 3) % 4,
                    4: ((prompt_index +1) - 4) % 4,
                }

                for start, remainder in remainders.items():
                    if (prompt_index +1) >= start and remainder == 0:  # Make sure number is >= starting value.
                        image_number = start
                    
                image_downloaded = download_image(driver, prompt, image_dir=image_dir,image_number=image_number)

                if not image_downloaded:
                    logging.warning(f"Failed to download image for prompt: {prompt}")
                    break

                logging.info(f"Processed prompt: {prompt}")
                prompt_index += 1 # Important: Increment the prompt index to know which prompt to execute next
                local_image_count += 1  # one execution generates 1 image, we already know.

            except Exception as e:
                logging.error(f"❌ Error during prompt processing: {e}")
                break # Break this inner loop and move to new chrome instance

        # Clean Up
        logging.info("Cleaning up and closing the driver...")
        driver.quit()
        shutil.rmtree(temp_profile_dir, ignore_errors=True)

        email_counter += 1# Important: Incremet the Email to Login to new Id

    logging.info("Automation script finished.")
    return email_counter


def process_reels(base_folder): #makes a list of paths of reel folders
    reel_paths = []
    for reel_folder in os.listdir(base_folder): #get path of each folder one by one
        if reel_folder.isdigit():  #checks if its a folder of reel or not 
            reel_paths.append(os.path.join(base_folder, reel_folder))

    return reel_paths

def multi_fn(data_list):
    base_email, password, reel_folder, start_id = data_list
    prompt_file_path = os.path.join(reel_folder, "prompts.txt")
    automate_piclumen(prompt_file_path, base_email, password, reel_folder,start_id)

# Example Usage
if __name__ == "__main__":
    # Needs Install Requests
    try:
        import requests
        print(requests.__version__)
    except ImportError:
        print("requests is not installed")
        exit()

    base_folder = input("Enter Base Folder:-")
    base_email = "anshika477422"  # Replace with your base email
    password = "Hello_word"  # Replace with your password
    


    start_id = int(input("Enter the starting email ID: ")) #Asks for user the starting id
    reel_folders = process_reels(base_folder)
    data_list = [
        (base_email, password, reel_folders[i], start_id + i*10 )
        for i in range(len(reel_folders))
    ]
    
    with ProcessPoolExecutor(max_workers=6) as executor:
        results = executor.map(multi_fn, data_list)



    
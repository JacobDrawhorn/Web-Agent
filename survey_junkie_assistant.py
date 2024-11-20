from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import os
from dotenv import load_dotenv

class SurveyJunkieAssistant:
    def __init__(self):
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-notifications')
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment variables
        self.email = os.getenv('SURVEYJUNKIE_EMAIL')
        self.password = os.getenv('SURVEYJUNKIE_PASSWORD')

    def login(self):
        """Login to SurveyJunkie"""
        try:
            # Navigate to SurveyJunkie
            self.driver.get('https://www.surveyjunkie.com/login')
            
            # Wait for login form and enter credentials
            email_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'email')))
            email_input.send_keys(self.email)
            
            password_input = self.driver.find_element(By.NAME, 'password')
            password_input.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            login_button.click()
            
            # Wait for dashboard to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'dashboard')))
            print("Successfully logged in!")
            
        except TimeoutException:
            print("Failed to login. Please check your credentials or internet connection.")
            self.close()
            return False
        return True

    def find_available_surveys(self):
        """Find and print available surveys"""
        try:
            # Wait for surveys to load
            surveys = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.survey-item')))
            
            print("\nAvailable Surveys:")
            for idx, survey in enumerate(surveys, 1):
                try:
                    points = survey.find_element(By.CSS_SELECTOR, '.points').text
                    duration = survey.find_element(By.CSS_SELECTOR, '.duration').text
                    print(f"{idx}. Points: {points} - Duration: {duration}")
                except:
                    continue
            
            return surveys
        except TimeoutException:
            print("No surveys found or page failed to load.")
            return []

    def start_survey(self, survey_element):
        """Start a specific survey"""
        try:
            # Click on the survey
            survey_element.click()
            
            # Wait for survey to load in new window
            self.wait.until(EC.number_of_windows_to_be(2))
            
            # Switch to new window
            new_window = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_window)
            
            print("Survey loaded! Please complete the survey manually.")
            print("The script will wait until you're done.")
            input("Press Enter when you've completed the survey...")
            
            # Close survey window and switch back to main window
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        except Exception as e:
            print(f"Error starting survey: {str(e)}")

    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    assistant = SurveyJunkieAssistant()
    
    if not assistant.login():
        return
    
    try:
        while True:
            print("\nOptions:")
            print("1. Find available surveys")
            print("2. Refresh page")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                surveys = assistant.find_available_surveys()
                if surveys:
                    survey_choice = input("\nEnter survey number to start (or 0 to go back): ")
                    try:
                        survey_idx = int(survey_choice) - 1
                        if 0 <= survey_idx < len(surveys):
                            assistant.start_survey(surveys[survey_idx])
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            
            elif choice == '2':
                assistant.driver.refresh()
                print("Page refreshed!")
            
            elif choice == '3':
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    finally:
        assistant.close()

if __name__ == "__main__":
    main()

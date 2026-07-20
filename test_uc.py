import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--headless=new")
try:
    driver = uc.Chrome(options=options)
    print("Success!")
    driver.quit()
except Exception as e:
    print(f"Error: {e}")

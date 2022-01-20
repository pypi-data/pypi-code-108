
import requests
import time

def import_jquer(driver, debug=False):
    jquery = requests.get("https://code.jquery.com/jquery-1.12.4.min.js").text
    time.sleep(0.5)
    driver.execute_script(jquery)
    if debug:
        driver.execute_script("""
            if (window.jQuery) {  
                // jQuery is loaded  
                alert("Yeah!");
            } else {
                // jQuery is not loaded
                alert("Doesn't Work");
            }
        """)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import threading
import os
from pathlib import Path

class BrowserAutomation:
    def __init__(self):
        self.apkpure_driver = None
        self.uptodown_driver = None
        self.apkpure_tabs = []
        self.uptodown_tabs = []
        self.downloads_path = str(Path.home() / "Downloads")
        
    def cleanup_downloads(self):
        """حذف ملفات APK التي تحتوي على كلمة 'black' في اسمها من مجلد التنزيلات"""
        try:
            for filename in os.listdir(self.downloads_path):
                if filename.lower().endswith('.apk') and 'black' in filename.lower():
                    file_path = os.path.join(self.downloads_path, filename)
                    try:
                        os.remove(file_path)
                        print(f"تم حذف الملف: {filename}")
                    except Exception as e:
                        print(f"فشل في حذف الملف {filename}: {str(e)}")
        except Exception as e:
            print(f"حدث خطأ أثناء تنظيف مجلد التنزيلات: {str(e)}")

    def create_driver(self):
        """إنشاء متصفح"""
        try:
            edge_options = EdgeOptions()
            edge_service = EdgeService(EdgeChromiumDriverManager().install())
            return webdriver.Edge(service=edge_service, options=edge_options)
           
        except:
            try:
                firefox_options = FirefoxOptions()
                firefox_service = FirefoxService(GeckoDriverManager().install())
                return webdriver.Firefox(service=firefox_service, options=firefox_options)
            except:
                try:
                    chrome_options = ChromeOptions()
                    chrome_service = ChromeService(ChromeDriverManager().install())
                    return webdriver.Chrome(service=chrome_service, options=chrome_options)
                except:
                    raise Exception("لم يتم العثور على متصفح مدعوم")

    def visit_apkpure(self, tab_index):
        """زيارة موقع APKPure بشكل متكرر"""
        while True:
            try:
                self.apkpure_driver.switch_to.window(self.apkpure_tabs[tab_index])
                self.apkpure_driver.get("https://d.apkpure.com/b/APK/com.blacklotus.app?version=latest")
                time.sleep(0.5)
            except:
                continue

    def visit_uptodown(self, tab_index):
        """زيارة موقع Uptodown وتحميل التطبيق"""
        try:
            self.uptodown_driver.switch_to.window(self.uptodown_tabs[tab_index])
            self.uptodown_driver.get("https://black-lotus.en.uptodown.com/android/download")
            time.sleep(5)
            
            download_button = WebDriverWait(self.uptodown_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#detail-download-button"))
            )
            download_button.click()
            print(f"تم النقر على زر التحميل في التبويب {tab_index}")
            
        except Exception as e:
            print(f"حدث خطأ في التبويب {tab_index}: {str(e)}")

    def run(self):
        """تشغيل البرنامج الرئيسي"""
        self.cleanup_downloads()
        
        # إنشاء نافذتين منفصلتين
        print("جاري إنشاء نافذة APKPure...")
        self.apkpure_driver = self.create_driver()
        print("جاري إنشاء نافذة Uptodown...")
        self.uptodown_driver = self.create_driver()
        
        # فتح 10 تبويبات في نافذة APKPure
        self.apkpure_tabs.append(self.apkpure_driver.current_window_handle)
        for _ in range(9):
            self.apkpure_driver.execute_script("window.open('');")
            self.apkpure_tabs.append(self.apkpure_driver.window_handles[-1])
        
        # فتح 10 تبويبات في نافذة Uptodown
        self.uptodown_tabs.append(self.uptodown_driver.current_window_handle)
        for _ in range(9):
            self.uptodown_driver.execute_script("window.open('');")
            self.uptodown_tabs.append(self.uptodown_driver.window_handles[-1])

        threads = []
        
        # تشغيل تبويبات APKPure
        for i in range(10):
            thread = threading.Thread(target=self.visit_apkpure, args=(i,))
            threads.append(thread)
            thread.start()

        # تشغيل تبويبات Uptodown
        for i in range(10):
            thread = threading.Thread(target=self.visit_uptodown, args=(i,))
            threads.append(thread)
            thread.start()

        # تشغيل عملية التنظيف الدورية
        cleanup_thread = threading.Thread(target=self.periodic_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()

        # انتظار انتهاء جميع threads
        for thread in threads:
            thread.join()

    def periodic_cleanup(self):
        """تنظيف دوري لمجلد التنزيلات كل 5 ثواني"""
        while True:
            self.cleanup_downloads()
            time.sleep(5)

    def cleanup(self):
        """إغلاق المتصفحات"""
        if self.apkpure_driver:
            try:
                self.apkpure_driver.quit()
            except:
                pass
        if self.uptodown_driver:
            try:
                self.uptodown_driver.quit()
            except:
                pass

if __name__ == "__main__":
    try:
        automation = BrowserAutomation()
        automation.run()
    except KeyboardInterrupt:
        print("\nإيقاف البرنامج...")
    finally:
        automation.cleanup()

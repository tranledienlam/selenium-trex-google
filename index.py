import argparse
from selenium_browserkit import BrowserManager, Node, By, Utility

from googl import Auto as AutoGoogle, Setup as SetupGoogle
PROJECT_URL = "https://www.trex.xyz/portal"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
        self.run()

    def run(self):
        # SetupGoogle(self.node, self.profile).run()
        self.node.go_to(f'https://s.trex.xyz/lltc35', method="get")
        Utility.wait_time(10)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.auto_google = AutoGoogle(node, profile)
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

        self.run()

    def check_login(self):
        self.node.wait_for_disappear(By.XPATH, '//*[contains(@id, "__lottie_element_")]')
        text_check = self.node.has_texts(['Login or Sign Up', 'Daily Check in', 'TOTAL BADGES'])
        if 'Login or Sign Up' in text_check:
            self.node.log('Chưa đăng nhập')
            return False
        elif 'Daily Check in' in text_check or 'TOTAL BADGES' in text_check:
            self.node.log('Đã đăng nhập')
            return True
        else:
            self.node.log('Không thể kiểm tra đăng nhập')
            return None

    def login(self):
        is_login = self.check_login()
        if is_login == True:
            return True
        elif is_login == False:
            self.node.find_and_click(By.XPATH, '//span[normalize-space(text()) = "google"]')
            self.auto_google.confirm_login()
            self.node.go_to(f'{PROJECT_URL}/quest', method="get")
            return self.check_login()
        else:
            return None

    def check_in_daily(self):
        for _ in range(2):
            url = self.node.get_url()
            if 'quest' not in url:
                self.node.go_to(f'{PROJECT_URL}/quest', method="get")
            else:
                break
        if self.node.find_and_click(By.XPATH, '//button[not(@disabled) and contains(text(),"Check in")]'):
            return True
        else:
            return False

    def run(self):
        completed = []
        if not self.auto_google.run():
            self.node.log('Không thể đăng nhập Google')
            return

        self.node.go_to(f'{PROJECT_URL}/quest', method="get")
        if not self.login():
            self.node.log('Không thể đăng nhập')
            return
        if self.check_in_daily():
            completed.append('check-in')
            
        self.node.snapshot(f'Hoàn thành: {completed}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')

    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(
                        headless=args.headless,
                        disable_gpu=args.disable_gpu,
                        use_tele=True
                    )
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )
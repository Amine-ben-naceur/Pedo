import sys
import requests
from requests.exceptions import RequestException
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QLineEdit, QPushButton, QLabel, QWidget, QVBoxLayout, QToolBar, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap

# Bing API Key
BING_API_KEY = "your bing api here " 

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pedoفيل")
        self.resize(1024, 768)
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.toggle_toolbar_search)
        self.setCentralWidget(self.tabs)
        self.setup_toolbar()
        self.setup_home_page()

    def enable_tor_proxy(self, use_proxy=True):
        """Enable or disable Tor SOCKS5 proxy."""
        if use_proxy:
            print("Enabling Tor Proxy...")
            proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, "127.0.0.1", 9050)
        else:
            print("Disabling Proxy...")
            proxy = QNetworkProxy()
        QNetworkProxy.setApplicationProxy(proxy)

    def setup_toolbar(self):
        """Set up navigation toolbar."""
        self.toolbar = QToolBar("Navigation", self)
        self.addToolBar(self.toolbar)

        button_style = """
            QPushButton {
                background-color: #5e2b8e;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7c3d9b;
            }
        """

        back_btn = QPushButton("<")
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet(button_style)
        self.toolbar.addWidget(back_btn)

        forward_btn = QPushButton(">")
        forward_btn.clicked.connect(self.go_forward)
        forward_btn.setStyleSheet(button_style)
        self.toolbar.addWidget(forward_btn)

        refresh_btn = QPushButton("⟳")
        refresh_btn.clicked.connect(self.refresh_page)
        refresh_btn.setStyleSheet(button_style)
        self.toolbar.addWidget(refresh_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search query...")
        self.url_bar.returnPressed.connect(self.search_or_load)
        self.url_bar.setStyleSheet("""
            background-color: #3b1b6f;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        """)
        self.toolbar.addWidget(self.url_bar)

        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(self.add_new_tab)
        new_tab_btn.setStyleSheet(button_style)
        self.toolbar.addWidget(new_tab_btn)

    def setup_home_page(self):
        """Set up the home page with a large logo."""
        home_widget = QWidget()
        layout = QVBoxLayout()

        logo = QLabel()
        pixmap = QPixmap("C:/Users/mamou/OneDrive/Bureau/pedo3/logo.png").scaled(400, 400, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        home_widget.setStyleSheet("""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #5e2b8e);
            color: white;
            font-family: Arial, sans-serif;
        """)
        home_widget.setLayout(layout)
        self.tabs.addTab(home_widget, "Home")

    def toggle_toolbar_search(self):
        """Hide the search bar on the home page; show it elsewhere."""
        if self.tabs.currentIndex() == 0:  # Home page
            self.url_bar.hide()
        else:
            self.url_bar.show()

    def add_new_tab(self, url=None):
        """Add a new tab with multimedia support."""
        browser = QWebEngineView()

        browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

        browser.setUrl(QUrl(url if url else "about:blank"))
        browser.urlChanged.connect(self.update_url_bar)
        browser.loadFinished.connect(self.on_load_finished)

        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        """Close the selected tab."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_url_bar(self, url):
        """Update the URL bar and tab name."""
        self.url_bar.setText(url.toString(QUrl.RemoveScheme | QUrl.RemovePassword))
        current_tab_index = self.tabs.currentIndex()
        self.tabs.setTabText(current_tab_index, url.host() or "New Tab")

    def on_load_finished(self, success):
        """Handle page load completion."""
        if not success:
            QMessageBox.warning(self, "Error", "Page failed to load.")

    def go_back(self):
        """Go back in the current tab."""
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QWebEngineView) and current_tab.history().canGoBack():
            current_tab.back()

    def go_forward(self):
        """Go forward in the current tab."""
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QWebEngineView) and current_tab.history().canGoForward():
            current_tab.forward()

    def refresh_page(self):
        """Reload the current tab."""
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QWebEngineView):
            current_tab.reload()

    def search_or_load(self):
        """Handle search bar input."""
        query = self.url_bar.text()
        if "." in query and not query.startswith("http"):
            if query.endswith(".onion"):
                self.enable_tor_proxy(use_proxy=True)
                url = "http://" + query
            else:
                self.enable_tor_proxy(use_proxy=False)
                url = "http://" + query
            self.load_url_in_current_tab(url)
        else:
            self.perform_search(query)

    def load_url_in_current_tab(self, url):
        """Load a URL in the current tab."""
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QWebEngineView):
            current_tab.setUrl(QUrl(url))
        else:
            self.tabs.removeTab(0) 
            self.add_new_tab(url)  

    def perform_search(self, query):
        """Perform a Bing search and display results."""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
            params = {"q": query, "count": 10}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            search_results = data.get("webPages", {}).get("value", [])
            html_content = "<h1>Search Results:</h1><ul>"
            for result in search_results:
                html_content += f'<li><a href="{result["url"]}">{result["name"]}</a></li>'
            html_content += "</ul>"

           
            current_tab = self.tabs.currentWidget()
            if isinstance(current_tab, QWebEngineView):
                current_tab.setHtml(html_content)
            else:
                self.add_new_tab("about:blank")
        except RequestException as e:
            QMessageBox.critical(self, "Error", f"Search failed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec_())

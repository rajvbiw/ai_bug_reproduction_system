#!/usr/bin/env python
"""
Playwright-based automated live demo system for the AI Bug Reproduction System.
Runs a visual workflow directly in the browser and displays PASS/FAIL feedback.
"""

import os
import sys
import time
import argparse

def generate_test_assets():
    """Generates dummy files for log and screenshot analysis testing."""
    from PIL import Image
    print("[+] Generating dummy log and screenshot assets...")
    
    # 1. Dummy Traceback Log File
    with open("demo_test_log.txt", "w", encoding="utf-8") as f:
        f.write(
            "Traceback (most recent call last):\n"
            "  File \"app/backend/services/tasks.py\", line 76, in process_bug_report\n"
            "    exec_result = runner.run_test(test_file, repo_path)\n"
            "  File \"sandbox/docker_runner/runner.py\", line 15, in run_test\n"
            "    raise ConnectionError(\"Failed to connect to Docker socket at /var/run/docker.sock\")\n"
            "ConnectionError: Failed to connect to Docker socket at /var/run/docker.sock\n"
        )
    print("  - Generated demo_test_log.txt")

    # 2. Dummy 100x100 PNG image
    img = Image.new("RGB", (100, 100), color=(138, 43, 226)) # Purple color
    img.save("demo_screenshot.png")
    print("  - Generated demo_screenshot.png")

def cleanup_test_assets():
    """Cleans up the generated dummy files."""
    print("[+] Cleaning up dummy assets...")
    for filename in ["demo_test_log.txt", "demo_screenshot.png"]:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"  - Removed {filename}")
            except Exception as e:
                print(f"  - Warning: Failed to remove {filename}: {e}")

def check_and_install_dependencies():
    """Checks for required dependencies and installs them if missing."""
    import subprocess
    
    needed = []
    try:
        import PIL
    except ImportError:
        needed.append("pillow")
        
    try:
        import playwright
    except ImportError:
        needed.append("playwright")
        
    if needed:
        print(f"[+] Missing dependencies detected: {', '.join(needed)}. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + needed)
            print("[+] Installation successful.")
        except Exception as e:
            print(f"[!] Failed to install dependencies via pip: {e}")
            sys.exit(1)
            
    if "playwright" in needed:
        print("[+] Installing Chromium browser binaries for Playwright...")
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("[+] Chromium binaries installed successfully.")
        except Exception as e:
            print(f"[!] Failed to install Playwright Chromium binaries: {e}")
            sys.exit(1)

def run_demo(url, slow_mo, headless_mode):
    check_and_install_dependencies()
    # Dynamic imports of Playwright to avoid dependency issues if not installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Playwright is not installed. Please run: pip install playwright && playwright install chromium")
        sys.exit(1)

    generate_test_assets()
    
    exit_code = 0
    
    print(f"[+] Starting Playwright live demo on {url} (Slow-mo: {slow_mo}ms, Headless: {headless_mode})")
    
    with sync_playwright() as p:
        browser = None
        try:
            # Launch Chrome/Chromium
            browser = p.chromium.launch(
                headless=headless_mode,
                slow_mo=slow_mo
            )
            
            context = browser.new_context(
                viewport={"width": 1440, "height": 900}
            )
            page = context.new_page()
            
            # --- HELPER FUNCTIONS FOR VISUAL OVERLAY ---
            def inject_progress_overlay():
                page.evaluate("""() => {
                    if (document.getElementById('demo-overlay')) return;

                    const style = document.createElement('style');
                    style.innerHTML = `
                        @keyframes demo-pulse {
                            0% { transform: scale(1); }
                            50% { transform: scale(1.02); }
                            100% { transform: scale(1); }
                        }
                        .demo-step-running {
                            color: #3b82f6 !important;
                            opacity: 1 !important;
                            font-weight: 600;
                        }
                        .demo-step-completed {
                            color: #10b981 !important;
                            opacity: 1 !important;
                        }
                        .demo-step-failed {
                            color: #ef4444 !important;
                            opacity: 1 !important;
                            font-weight: bold;
                        }
                    `;
                    document.head.appendChild(style);

                    const overlay = document.createElement('div');
                    overlay.id = 'demo-overlay';
                    overlay.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        z-index: 99999;
                        background: rgba(15, 15, 25, 0.95);
                        border: 2px solid #8a2be2;
                        border-radius: 16px;
                        padding: 24px;
                        color: #e0e0e0;
                        font-family: 'Inter', sans-serif;
                        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
                        width: 340px;
                        backdrop-filter: blur(12px);
                        transition: all 0.3s ease;
                    `;
                    overlay.innerHTML = `
                        <h3 style="
                            margin: 0 0 16px 0;
                            color: #a855f7;
                            font-family: 'Outfit', sans-serif;
                            font-weight: 600;
                            font-size: 1.2rem;
                            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
                            padding-bottom: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                        ">
                            <span>Demo Control Panel</span>
                            <span id="demo-status-badge" style="
                                font-size: 0.75rem;
                                padding: 4px 10px;
                                border-radius: 20px;
                                background: #8a2be2;
                                color: #ffffff;
                                font-weight: bold;
                                letter-spacing: 0.5px;
                            ">RUNNING</span>
                        </h3>
                        <ul style="
                            list-style: none;
                            padding-left: 0;
                            margin: 0;
                        " id="demo-steps-list">
                            <li id="step-nav" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Navigate to App Dashboard</span>
                            </li>
                            <li id="step-bug" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Submit Bug Report</span>
                            </li>
                            <li id="step-chat" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Test AI Chatbot Assistant</span>
                            </li>
                            <li id="step-log" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Test Paste Log Analysis</span>
                            </li>
                            <li id="step-log-file" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Test Log File Upload</span>
                            </li>
                            <li id="step-screenshot" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Test Screenshot OCR Analysis</span>
                            </li>
                            <li id="step-github" style="margin-bottom: 12px; opacity: 0.5; display: flex; align-items: center; font-size: 0.95rem;">
                                <span class="icon" style="margin-right: 10px; font-size: 1.1rem;">⏳</span>
                                <span>Test GitHub Sync & Auto-Analyze</span>
                            </li>
                        </ul>
                        <div id="demo-result-banner" style="
                            margin-top: 20px;
                            padding: 12px;
                            border-radius: 8px;
                            text-align: center;
                            font-weight: 600;
                            font-size: 1rem;
                            display: none;
                            animation: demo-pulse 2s infinite;
                        "></div>
                    `;
                    document.body.appendChild(overlay);
                }""")

            def update_step(step_id, status, text=None):
                icon = "⏳"
                classname = ""
                if status == "running":
                    icon = "🔄"
                    classname = "demo-step-running"
                elif status == "completed":
                    icon = "✅"
                    classname = "demo-step-completed"
                elif status == "failed":
                    icon = "❌"
                    classname = "demo-step-failed"
                
                text_json = f'"{text}"' if text else "null"
                page.evaluate(f"""
                    const li = document.getElementById('{step_id}');
                    if (li) {{
                        li.className = '{classname}';
                        li.querySelector('.icon').innerText = '{icon}';
                        if ({text_json}) {{
                            li.querySelector('span:not(.icon)').innerText = {text_json};
                        }}
                    }}
                """)

            def show_final_result(passed, error_msg=""):
                if passed:
                    badge_bg = "#10b981"
                    badge_text = "PASS"
                    banner_bg = "rgba(16, 185, 129, 0.15)"
                    banner_border = "1px solid #10b981"
                    banner_color = "#10b981"
                    banner_text = "🎉 DEMO PASSED SUCCESSFULLY!"
                else:
                    badge_bg = "#ef4444"
                    badge_text = "FAIL"
                    banner_bg = "rgba(239, 68, 68, 0.15)"
                    banner_border = "1px solid #ef4444"
                    banner_color = "#ef4444"
                    banner_text = f"❌ DEMO FAILED: {error_msg}"
                
                page.evaluate(f"""
                    const badge = document.getElementById('demo-status-badge');
                    if (badge) {{
                        badge.innerText = '{badge_text}';
                        badge.style.background = '{badge_bg}';
                    }}
                    const banner = document.getElementById('demo-result-banner');
                    if (banner) {{
                        banner.innerText = `{banner_text}`;
                        banner.style.background = '{banner_bg}';
                        banner.style.border = '{banner_border}';
                        banner.style.color = '{banner_color}';
                        banner.style.display = 'block';
                    }}
                """)

            # --- STEP 1: NAVIGATION ---
            print("[+] Executing Step 1: Navigate to Dashboard...")
            try:
                page.goto(url, timeout=15000)
            except Exception as e:
                print(f"[!] Target URL {url} is not accessible. Make sure your project is running (docker-compose up --build)")
                raise ConnectionError(f"Could not connect to {url}: {e}")
                
            inject_progress_overlay()
            update_step("step-nav", "running")
            
            # Verify we are on the dashboard
            page.wait_for_selector("#dashboard-view", state="visible", timeout=5000)
            update_step("step-nav", "completed")
            time.sleep(1.5)

            # --- STEP 2: SUBMIT BUG REPORT ---
            print("[+] Executing Step 2: Submit Bug Report...")
            update_step("step-bug", "running")
            
            # Click navigation to submit view
            page.click('[data-view="submit"]')
            page.wait_for_selector("#submit-view", state="visible", timeout=5000)
            
            # Fill out form
            bug_title = f"Division by zero in math module - {int(time.time())}"
            page.fill("#title", bug_title)
            page.fill("#description", "The system crashed when calling standard math divide module with denominator as 0.")
            page.fill("#repository_url", "https://github.com/example/math-module")
            page.fill("#target_branch", "main")
            
            time.sleep(1.0)
            # Submit bug report
            page.click('#bug-form button[type="submit"]')
            
            # Wait to navigate back to dashboard automatically
            page.wait_for_selector("#dashboard-view", state="visible", timeout=5000)
            
            # Verify the submitted bug appears in the bugs table
            page.wait_for_selector(f"text={bug_title}", state="visible", timeout=8000)
            update_step("step-bug", "completed")
            time.sleep(1.5)

            # --- STEP 3: AI CHATBOT ASSISTANT ---
            print("[+] Executing Step 3: Test AI Chatbot...")
            update_step("step-chat", "running")
            
            # Navigate to Chat view
            page.click('[data-view="chat"]')
            page.wait_for_selector("#chat-view", state="visible", timeout=5000)
            
            # Type and send prompt
            chat_prompt = "How can I catch ZeroDivisionError in Python calculations?"
            page.fill("#chat-input", chat_prompt)
            time.sleep(0.5)
            page.click("#chat-send-btn")
            
            # Verify message gets added and the thinking status resolves
            # Wait for user message to appear
            page.wait_for_selector(f"text={chat_prompt}", state="visible", timeout=5000)
            
            # Wait for the chatbot to finish streaming (Wait until the last assistant response doesn't contain "Thinking...")
            # We can use a custom function/selector to verify
            time.sleep(1.5) # Wait for stream start
            page.wait_for_function("""
                () => {
                    const messages = document.querySelectorAll('#chat-history-container .chat-message.assistant');
                    if (messages.length === 0) return false;
                    const lastMessage = messages[messages.length - 1];
                    return lastMessage && !lastMessage.innerText.includes('Thinking...');
                }
            """, timeout=15000)
            
            update_step("step-chat", "completed")
            time.sleep(1.5)

            # --- STEP 4: PASTE TEXT LOG ANALYSIS ---
            print("[+] Executing Step 4: Test Paste Log Analysis...")
            update_step("step-log", "running")
            
            # Navigate to Log Analyzer
            page.click('[data-view="analyze"]')
            page.wait_for_selector("#analyze-view", state="visible", timeout=5000)
            
            # Click Paste Text tab to ensure it's active
            page.click('[data-tab="tab-text"]')
            
            # Paste Traceback logs
            traceback_text = (
                "Traceback (most recent call last):\n"
                "  File \"math_module.py\", line 12, in divide_numbers\n"
                "    res = numerator / denominator\n"
                "ZeroDivisionError: division by zero"
            )
            page.fill("#log-text-input", traceback_text)
            time.sleep(0.5)
            
            # Submit Log Analysis
            page.click("#analyze-text-btn")
            
            # Wait for results summary to change from default ("No active analysis")
            page.wait_for_function("""
                () => {
                    const summary = document.getElementById('result-summary').innerText;
                    return summary && !summary.includes('No active analysis');
                }
            """, timeout=15000)
            
            # Verify severity and root cause are populated
            severity = page.inner_text("#results-severity")
            root_cause = page.inner_text("#result-cause")
            
            print(f"  - Pasted Log Analysis: Severity={severity}, Cause={root_cause}")
            if not severity or severity == "--" or not root_cause or root_cause == "--":
                raise ValueError("Paste Log Analysis failed to populate severity or root cause values.")
                
            update_step("step-log", "completed")
            time.sleep(1.5)

            # --- STEP 5: LOG FILE UPLOAD ---
            print("[+] Executing Step 5: Test Log File Upload...")
            update_step("step-log-file", "running")
            
            # Navigate to File Upload tab
            page.click('[data-tab="tab-file"]')
            
            # Select the dummy log file generated earlier
            page.set_input_files('#log-file-input', 'demo_test_log.txt')
            time.sleep(0.5)
            
            # Verify file name updates in drop zone
            page.wait_for_selector("text=Loaded: demo_test_log.txt", state="visible", timeout=5000)
            
            # Run Log File Analysis
            page.click("#analyze-file-btn")
            
            # Wait for results to be analyzed
            time.sleep(1.0)
            page.wait_for_function("""
                () => {
                    const summary = document.getElementById('result-summary').innerText;
                    return summary && !summary.includes('Analyzing...');
                }
            """, timeout=15000)
            
            # Check results
            severity = page.inner_text("#results-severity")
            root_cause = page.inner_text("#result-cause")
            print(f"  - File Log Analysis: Severity={severity}, Cause={root_cause}")
            if not severity or severity == "--" or not root_cause or root_cause == "--":
                raise ValueError("File Log Analysis failed to populate values.")
                
            update_step("step-log-file", "completed")
            time.sleep(1.5)

            # --- STEP 6: SCREENSHOT OCR ANALYSIS ---
            print("[+] Executing Step 6: Test Screenshot OCR Analysis...")
            update_step("step-screenshot", "running")
            
            # Navigate to Screenshot/OCR tab
            page.click('[data-tab="tab-ocr"]')
            
            # Upload dummy screenshot PNG
            page.set_input_files('#ocr-file-input', 'demo_screenshot.png')
            time.sleep(0.5)
            
            # Verify image name updates in drop zone
            page.wait_for_selector("text=Loaded Image: demo_screenshot.png", state="visible", timeout=5000)
            
            # Click OCR Analysis Button
            page.click("#analyze-ocr-btn")
            
            # Wait for results
            time.sleep(1.0)
            page.wait_for_function("""
                () => {
                    const summary = document.getElementById('result-summary').innerText;
                    return summary && !summary.includes('Processing OCR...');
                }
            """, timeout=15000)
            
            # Verify OCR section displays and results populate
            page.wait_for_selector("#extracted-text-section", state="visible", timeout=5000)
            ocr_text = page.inner_text("#result-ocr-text")
            print(f"  - OCR Extracted Text: {ocr_text[:80]}...")
            if not ocr_text:
                raise ValueError("OCR Screenshot extraction returned empty result.")
                
            update_step("step-screenshot", "completed")
            time.sleep(1.5)

            # --- STEP 7: GITHUB SYNC & AUTO-ANALYZE ---
            print("[+] Executing Step 7: Test GitHub Import & Auto-Analyze...")
            update_step("step-github", "running")
            
            # Navigate to GitHub Sync view
            page.click('[data-view="github"]')
            page.wait_for_selector("#github-view", state="visible", timeout=5000)
            
            # Fill in repo details and issue number
            page.fill("#github-repo", "facebook/react")
            page.fill("#github-issue-number", "42")
            time.sleep(0.5)
            
            # Submit import
            page.click("#github-submit-btn")
            
            # Wait for status results box to display import info
            page.wait_for_selector("#github-results", state="visible", timeout=15000)
            
            # Verify the reproduction plan details are visible in the page
            page.wait_for_selector("text=AI Reproduction Plan", state="visible", timeout=5000)
            status_text = page.inner_text("#github-status-box")
            print(f"  - GitHub Sync Import Status: {status_text[:100]}...")
            
            update_step("step-github", "completed")
            time.sleep(2.0)
            
            # Show final PASS results on the panel overlay
            print("[+] All steps completed successfully!")
            show_final_result(passed=True)
            time.sleep(5.0)  # Hold the browser open so user can witness the PASS banner

        except Exception as err:
            exit_code = 1
            print(f"[FAIL] Demo failed: {err}")
            if browser and page:
                try:
                    show_final_result(passed=False, error_msg=str(err))
                    time.sleep(5.0)  # Hold open so failure banner is visible
                except Exception as eval_err:
                    print(f"    - Failed to display visual error in browser: {eval_err}")
        finally:
            if browser:
                browser.close()
                print("[+] Closed browser.")
                
    cleanup_test_assets()
    sys.exit(exit_code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Bug Reproduction System - Automated Playwright Live Demo")
    parser.add_argument("--url", type=str, default="http://localhost:8080", help="Frontend dashboard URL (default: http://localhost:8080)")
    parser.add_argument("--slow-mo", type=int, default=800, help="Playwright slow-mo step delay in ms (default: 800)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (default: False/visual)")
    
    args = parser.parse_args()
    
    # Run the demo
    run_demo(args.url, args.slow_mo, args.headless)

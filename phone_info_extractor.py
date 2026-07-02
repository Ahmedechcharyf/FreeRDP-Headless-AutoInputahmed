#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
استخراج معلومات عن رقم الهاتف - نسخة محسنة
Phone Information Extractor - Enhanced Version
المطور: Mahdi
المصدر: @DD_1_1_1
القناة: @iuron0
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from pyfiglet import Figlet
import colorama
from colorama import Fore, Back, Style
import sys
import os
from datetime import datetime

# ================== الألوان ==================
class Colors:
    """فئة لتنظيم الألوان"""
    # ألوان أساسية
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    GRAY = '\033[1;30m'
    
    # ألوان مع خلفية
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    
    # إعادة تعيين
    RESET = '\033[0m'
    
    @staticmethod
    def print_success(text):
        """طباعة رسالة نجاح"""
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    
    @staticmethod
    def print_error(text):
        """طباعة رسالة خطأ"""
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
    
    @staticmethod
    def print_warning(text):
        """طباعة رسالة تحذير"""
        print(f"{Colors.YELLOW}⚠️ {text}{Colors.RESET}")
    
    @staticmethod
    def print_info(text):
        """طباعة رسالة معلومات"""
        print(f"{Colors.CYAN}ℹ️ {text}{Colors.RESET}")

# ================== الدوال الرئيسية ==================

def get_info_phone(phone_number, operators):
    """
    استخراج معلومات الهاتف من phonenumbertrack.com
    
    Args:
        phone_number (str): رقم الهاتف
        operators (str): اسم المشغل
    
    Returns:
        str: معلومات الهاتف المنسقة
    """
    try:
        with requests.Session() as session:
            phone = requests.utils.quote(phone_number)
            url = f"https://www.phonenumbertrack.com/phone-number-track-trace-result?country=&phone={phone}&submit=#QueryResult"
            
            # إضافة timeout للطلب
            req = session.get(url, timeout=10).text
            soup = BeautifulSoup(req, "html.parser")
            
            tbody = soup.find("tbody")
            if not tbody:
                Colors.print_error("لم يتم العثور على البيانات!")
                return None
            
            kos = tbody.text
            details = soup.find("div", class_="row panel panel-default details")
            
            if not details:
                Colors.print_error("لم يتم العثور على تفاصيل!")
                return None
            
            koon = details.text
            
            # تنسيق البيانات
            formatted_data = format_phone_data(koon, kos, operators)
            return formatted_data
            
    except requests.exceptions.Timeout:
        Colors.print_error("انتهت مهلة الطلب - الموقع بطيء جداً")
        return None
    except requests.exceptions.ConnectionError:
        Colors.print_error("فشل الاتصال بالإنترنت")
        return None
    except Exception as e:
        Colors.print_error(f"حدث خطأ: {str(e)}")
        return None

def format_phone_data(details, summary, operators):
    """
    تنسيق بيانات الهاتف
    
    Args:
        details (str): التفاصيل الأساسية
        summary (str): الملخص
        operators (str): اسم المشغل
    
    Returns:
        str: البيانات المنسقة
    """
    formatted = details.replace("International Call Prefix", "📞 International Call Prefix")
    formatted = formatted.replace("Country Code", "\n🌍 Country Code")
    formatted = formatted.replace("(ایران)", "Iran (إيران)")
    formatted = formatted.replace("Area Code", "\n📍 Area Code")
    formatted = formatted.replace("Subscriber's Number", "\n👤 Subscriber's Number")
    
    formatted += "\n" + "="*50 + "\n"
    
    summary_formatted = summary.replace("Query", "🔍 Query")
    summary_formatted = summary_formatted.replace("Country ", "\n🌍 Country")
    summary_formatted = summary_formatted.replace("Phone Type", "\n📱 Phone Type")
    summary_formatted = summary_formatted.replace("Location", "\n📌 Location")
    summary_formatted = summary_formatted.replace("Operator", "\n🔌 Operator")
    summary_formatted = summary_formatted.replace("Advertising & Sponsored links", "")
    summary_formatted = summary_formatted.replace("More Options Check Phone Number", "")
    
    if "Operator" not in summary:
        summary_formatted += f"\n🔌 Known Provider: {operators}"
    
    return formatted + summary_formatted

def get_operator(phone_number):
    """
    الحصول على اسم مشغل الشبكة
    
    Args:
        phone_number (str): رقم الهاتف
    
    Returns:
        str: اسم المشغل
    """
    try:
        site = "https://www.celltrack.eu/site/trace"
        payload = {
            "_csrf": "J-sER_hYlIW2sj9tpjqyeYmDECR07hsR58zHHm5ILYNGpmIdnHXmvdrXd1n8d8A__9kiYw2bQUag_otXA2Vdsg==",
            "use-alt.flow": "1",
            "TrackForm[phone]": phone_number
        }
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        req = requests.post(site, headers=headers, data=payload, timeout=10)
        soup = BeautifulSoup(req.text, "html.parser")
        
        tbody_list = soup.find_all("tbody")
        if len(tbody_list) < 2:
            return "Unknown"
        
        rows = tbody_list[1].find_all("tr")
        if len(rows) < 2:
            return "Unknown"
        
        cells = rows[1].find_all("td")
        if len(cells) < 2:
            return "Unknown"
        
        operator = cells[1].text.replace(" ", "").replace("\n", "")
        return operator if operator else "Unknown"
        
    except requests.exceptions.Timeout:
        Colors.print_warning("مهلة الوقت انتهت عند البحث عن المشغل")
        return "Unknown"
    except Exception as e:
        Colors.print_warning(f"لم يتمكن من الحصول على المشغل: {str(e)}")
        return "Unknown"

def validate_phone_number(phone):
    """
    التحقق من صحة رقم الهاتف
    
    Args:
        phone (str): رقم الهاتف
    
    Returns:
        bool: هل الرقم صحيح
    """
    # يجب أن يبدأ برمز الدولة
    if not phone.startswith("+"):
        return False
    
    # يجب أن يحتوي على أرقام فقط بعد الرمز
    phone_digits = phone[1:]
    if not phone_digits.isdigit():
        return False
    
    # يجب أن يكون الرقم بين 10 و 15 رقم
    if not (10 <= len(phone_digits) <= 15):
        return False
    
    return True

def save_to_file(phone_number, data):
    """
    حفظ النتائج في ملف
    
    Args:
        phone_number (str): رقم الهاتف
        data (str): البيانات
    """
    try:
        # إنشاء مجلد للنتائج إن لم يكن موجوداً
        if not os.path.exists("results"):
            os.makedirs("results")
        
        filename = f"results/phone_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"رقم الهاتف: {phone_number}\n")
            f.write(f"التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(data)
        
        Colors.print_success(f"تم حفظ النتائج في: {filename}")
        return filename
        
    except Exception as e:
        Colors.print_error(f"فشل حفظ الملف: {str(e)}")
        return None

def display_logo():
    """عرض شعار التطبيق"""
    print(f"\n{Colors.CYAN}")
    print(Figlet(font="slant").renderText("PHONE INFO"))
    print(f"{Colors.YELLOW}استخراج معلومات رقم الهاتف - Phone Information Extractor{Colors.RESET}\n")
    print(f"{Colors.CYAN}المطور: Mahdi | القناة: @iuron0 | التلجرام: @DD_1_1_1{Colors.RESET}\n")
    print("="*60 + "\n")

def display_menu():
    """عرض القائمة الرئيسية"""
    print(f"\n{Colors.BLUE}===== القائمة الرئيسية ====={Colors.RESET}")
    print(f"{Colors.GREEN}1{Colors.RESET} - البحث عن رقم هاتف")
    print(f"{Colors.GREEN}2{Colors.RESET} - حول التطبيق")
    print(f"{Colors.GREEN}3{Colors.RESET} - خروج")
    print(f"{Colors.BLUE}==========================={Colors.RESET}\n")

def show_about():
    """عرض معلومات التطبيق"""
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"📱 استخراج معلومات رقم الهاتف")
    print(f"{'='*60}")
    print(f"\n{Colors.WHITE}الإصدار: 2.0")
    print(f"المطور: Mahdi")
    print(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"\n{Colors.YELLOW}الميزات:{Colors.RESET}")
    print(f"  ✅ البحث عن معلومات رقم الهاتف")
    print(f"  ✅ الحصول على مشغل الشبكة")
    print(f"  ✅ حفظ النتائج في ملف")
    print(f"  ✅ تصميم سهل الاستخدام")
    print(f"  ✅ معالجة الأخطاء")
    print(f"\n{Colors.YELLOW}التحذيرات:{Colors.RESET}")
    print(f"  ⚠️ استخدم البيانات بشكل قانوني")
    print(f"  ⚠️ احترم خصوصية الآخرين")
    print(f"  ⚠️ لا تستخدمها للتحرش")
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def main():
    """البرنامج الرئيسي"""
    try:
        while True:
            display_logo()
            display_menu()
            
            choice = input(f"{Colors.MAGENTA}اختر خياراً (1-3): {Colors.RESET}").strip()
            
            if choice == "1":
                # البحث عن رقم هاتف
                print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
                print(f"{Colors.YELLOW}📱 البحث عن معلومات رقم الهاتف{Colors.RESET}")
                print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
                
                phone = input(
                    f"{Colors.BLUE}أدخل رقم الهاتف مع رمز الدولة{Colors.RESET}\n"
                    f"{Colors.GREEN}مثال: +96477245345678{Colors.RESET}\n"
                    f"{Colors.MAGENTA}الرقم: {Colors.RESET}"
                ).strip()
                
                # التحقق من صحة الرقم
                if not validate_phone_number(phone):
                    Colors.print_error("رقم الهاتف غير صحيح!")
                    Colors.print_info("تأكد من:")
                    print(f"  • يبدأ بـ +")
                    print(f"  • يحتوي على أرقام فقط")
                    print(f"  • يكون بين 10 و 15 رقم")
                    input(f"\n{Colors.GRAY}اضغط Enter للمتابعة...{Colors.RESET}")
                    continue
                
                Colors.print_info("جاري البحث...")
                
                # الحصول على معلومات المشغل
                operator_name = get_operator(phone)
                Colors.print_success(f"مشغل الشبكة: {operator_name}")
                
                # الحصول على معلومات الهاتف
                phone_info = get_info_phone(phone, operator_name)
                
                if phone_info:
                    print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
                    print(f"{Colors.CYAN}{phone_info}{Colors.RESET}")
                    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}\n")
                    
                    # حفظ النتائج
                    save_choice = input(
                        f"{Colors.YELLOW}هل تريد حفظ النتائج؟ (y/n): {Colors.RESET}"
                    ).strip().lower()
                    
                    if save_choice == 'y':
                        save_to_file(phone, phone_info)
                
                input(f"\n{Colors.GRAY}اضغط Enter للمتابعة...{Colors.RESET}")
            
            elif choice == "2":
                # معلومات التطبيق
                show_about()
                input(f"{Colors.GRAY}اضغط Enter للمتابعة...{Colors.RESET}")
            
            elif choice == "3":
                # خروج
                print(f"\n{Colors.GREEN}شكراً لاستخدام التطبيق!{Colors.RESET}")
                print(f"{Colors.CYAN}القناة: @iuron0 | التلجرام: @DD_1_1_1{Colors.RESET}\n")
                break
            
            else:
                Colors.print_error("اختيار غير صحيح!")
                input(f"{Colors.GRAY}اضغط Enter للمتابعة...{Colors.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}تم إيقاف البرنامج من قبل المستخدم{Colors.RESET}\n")
    except Exception as e:
        Colors.print_error(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    main()

# حقوق المطور: Mahdi
# @DD_1_1_1 | @iuron0
# أداة تعليمية لاستخراج معلومات الهاتف من مصادر عامة
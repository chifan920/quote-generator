import streamlit as st
import datetime
import os
import base64
import pandas as pd

# 常數與配置
CONFIG = {
    "TAX_RATE": 0.05,
    "DEFAULT_HOURS": 3,
    "APP_TITLE": "專業攝影報價單生成系統",
    "APP_VERSION": "2.1.0",
}

# 報價細節資料結構
class ProjectData:
    # 台北攝影師報價行情及項目規格
    PROJECT_DETAILS = {
        "平面拍攝-活動": {
            "hourly_rate": 3500,  # 更新為3500/hr
            "video_options": False,
            "min_hours": 2,
            "category": "平面拍攝",
            "description": "適合企業活動、研討會等活動記錄",
        },
        "平面拍攝-品牌形象": {
            "hourly_rate": 4000,
            "video_options": False,
            "min_hours": 4,
            "category": "平面拍攝",
            "description": "適合品牌形象照片、產品展示等",
        },
        "平面拍攝-廣告代言": {
            "hourly_rate": 6000,
            "video_options": False,
            "min_hours": 4,
            "category": "平面拍攝",
            "description": "適合代言人拍攝、廣告素材拍攝等",
        },
        "平面拍攝-商品拍攝(時計費)": {
            "hourly_rate": 3500,
            "video_options": False,
            "min_hours": 3,
            "category": "平面拍攝",
            "description": "以時計費，適合需要多張照片用於社群媒體的商品拍攝",
            "planning_options": True,
        },
        "平面拍攝-商品拍攝(張計費)": {
            "hourly_rate": 5000,  # 代表每張的價格
            "video_options": False,
            "min_hours": 2,  # 這裡代表最少張數而非小時
            "category": "平面拍攝",
            "description": "以張計費，基本2張起，適合專業電商或廣告使用的高質量商品照",
            "per_photo": True,
            "planning_options": True,
        },
        "影像拍攝-短影音": {
            "hourly_rate": 15000,
            "video_options": True,
            "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
            "orientation_options": ['直式', '橫式'],
            "min_hours": 4,
            "category": "影像拍攝",
            "description": "適合社群短影音、品牌宣傳短片等",
        },
        "影像拍攝-訪談": {
            "hourly_rate": 12000,
            "video_options": True,
            "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
            "orientation_options": ['直式', '橫式'],
            "min_hours": 4,
            "category": "影像拍攝",
            "description": "適合人物專訪、意見領袖訪問等",
        },
        "影像拍攝-品牌形象": {
            "hourly_rate": 15000,
            "video_options": True,
            "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
            "orientation_options": ['直式', '橫式'],
            "min_hours": 4,
            "category": "影像拍攝",
            "description": "適合品牌形象影片、企業宣傳影片等",
        }
    }

    # 平面攝影加購品項選項
    ADD_ONS = {
        # 拍攝相關項目
        "拍攝相關": {
            "平面攝助": {
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "$2,000", "value": 2000},
                    {"label": "$2,500", "value": 2500},
                    {"label": "$3,000", "value": 3000},
                    {"label": "$4,000", "value": 4000},
                    {"label": "$5,000", "value": 5000},
                    {"label": "$6,000", "value": 6000},
                    {"label": "$8,000", "value": 8000}
                ],
                "spec": "協助拍攝、器材搬運、協調現場",
                "icon": "👤"
            },
            "燈光師": {
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "燈光師 $6,000", "value": 6000},
                    {"label": "燈光師 $8,000", "value": 8000},
                    {"label": "燈光師 $10,000", "value": 10000},
                    {"label": "燈光師 $12,000", "value": 12000},
                    {"label": "燈光師 $15,000", "value": 15000}
                ],
                "spec": "燈光設計與佈置",
                "icon": "🔦"
            },
            "燈光助理": {
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "$2,000", "value": 2000},
                    {"label": "$2,500", "value": 2500},
                    {"label": "$3,000", "value": 3000},
                    {"label": "$4,000", "value": 4000},
                    {"label": "$5,000", "value": 5000},
                    {"label": "$6,000", "value": 6000}
                ],
                "spec": "協助燈光設置與調整",
                "icon": "💡"
            },
            "燈光設備": {
                "type": "fixed",
                "description": "額外燈光設備費用",
                "unit": "式",
                "icon": "🔆"
            },
            "燈光": {
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "基本燈光 $3,000", "value": 3000},
                    {"label": "標準燈光 $4,000", "value": 4000},
                    {"label": "進階燈光 $5,000", "value": 5000},
                    {"label": "專業燈光 $6,000", "value": 6000}
                ],
                "spec": "燈光設備與人員綜合費用",
                "icon": "💡"
            },
            "美術": {  # 改名為美術
                "type": "fixed",
                "description": "美術人員費用",
                "unit": "位",
                "icon": "👨‍🎨",
                "spec": "協助場景陳設與美術規劃"
            }
        },
        
        # 美術道具相關項目
        "美術道具": {
            "美術道具費": {
                "type": "fixed",
                "description": "美術設計與道具費用",
                "unit": "式",
                "icon": "🎨",
                "actual_expense": True
            },
            "道具採買": {  # 簡化道具採買選項
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "$1,000", "value": 1000},
                    {"label": "$2,000", "value": 2000},
                    {"label": "$3,000", "value": 3000},
                    {"label": "$4,000", "value": 4000}
                ],
                "spec": "道具採買費用",
                "unit": "式",
                "icon": "🛒"
            },
            "企劃費": {
                "type": "fixed",
                "description": "拍攝前企劃與規劃費用",
                "unit": "式",
                "icon": "📝"
            }
        },
        
        # 後製相關項目
        "後製相關": {
            "提供小檔毛片": {  # 新增選項
                "type": "checkbox",
                "description": "提供小檔毛片(2MB/JPG)",
                "spec": "提供2MB JPG格式的原始拍攝檔案",
                "icon": "📸"
            },
            "網路用精修": {
                "type": "with_quantity",
                "price": 1000,
                "description": "網路用精修 $1,000/張",
                "spec": "適合網路發布使用的基礎修圖服務",
                "unit": "張",
                "icon": "🖼️"
            },
            "大圖精修": {
                "type": "with_quantity",
                "price": 2500,
                "description": "大圖精修 $2,500/張",
                "spec": "(1)修圖範圍: 皮膚修飾、身形美化、調光調色\n(不包含：商品電修/合成、人像合成、去背、服裝調整）\n(2)人像去背 +$2,500/張",
                "unit": "張",
                "icon": "✨"
            },
            "去背": {  # 新增去背選項
                "type": "with_quantity",
                "price": 300,
                "description": "去背 $300/張",
                "spec": "產品或人物去背服務",
                "unit": "張",
                "icon": "✂️"
            },
            "調光調色": {  # 修改調光調色選項
                "type": "dropdown",
                "options": [
                    {"label": "不需要", "value": 0},
                    {"label": "$3,500", "value": 3500},
                    {"label": "$7,000", "value": 7000}
                ],
                "spec": "全照片調光調色，提供6MB JPG檔",
                "unit": "式",
                "icon": "🎚️"
            },
            "現場出圖": {
                "type": "fixed",
                "description": "現場快速出圖服務",
                "unit": "式",
                "icon": "⚡",
                "with_quantity": True
            },
            "急件處理": {  # 新增急件處理選項
                "type": "fixed",
                "description": "急件處理費用",
                "unit": "式",
                "icon": "⏱️"
            }
        },
        
        # 場地相關項目
        "場地相關": {
            "攝影棚": {
                "type": "studio",
                "hours_options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "price_options": [
                    {"label": "$1,000/小時", "value": 1000},
                    {"label": "$1,200/小時", "value": 1200},
                    {"label": "$1,500/小時", "value": 1500},
                    {"label": "$1,800/小時", "value": 1800},
                    {"label": "$3,000/小時", "value": 3000}
                ],
                "spec": "攝影棚租借$1200/hr",
                "icon": "🏢"
            }
        },
        
        # 交通相關項目
        "交通相關": {
            "車馬費": {
                "type": "dropdown",
                "options": [
                    {"label": "$500", "value": 500},
                    {"label": "$1,000", "value": 1000},
                    {"label": "$1,500", "value": 1500},
                    {"label": "$2,000", "value": 2000},
                    {"label": "$2,500", "value": 2500},
                    {"label": "$3,000", "value": 3000}
                ],
                "spec": "交通車馬費",
                "icon": "🚗"
            }
        },
        
        # 優惠相關
        "優惠": {
            "折扣": {
                "type": "dropdown",
                "options": [
                    {"label": "無折扣", "value": 1.0},
                    {"label": "9折", "value": 0.9},
                    {"label": "8折", "value": 0.8},
                    {"label": "7折", "value": 0.7}
                ],
                "spec": "專案優惠折扣",
                "icon": "🏷️"
            }
        },
    }

    # 備註文字
    REMARKS = """※說明事項：
1. 拍攝前三週需提供詳細拍攝內容企劃，如拍攝規格變動請立刻告知，並依新需求供新報價單。
2. 拍攝需求如需購買一次性拍攝道具、美術陳設、協助購買道具、車馬費，費用另計。
3. 以時計費方案，時間包含前置至結束之時間，前置時間約1-1.5hr，如拍攝遇用餐時間，需提供餐盒。
4. 報價單有效期限為報價日期後四週。
5. 報價金額皆未稅。
6. 如於拍攝日前7日取消，需付總金額之30%製作費及已購買及租借之道具、器材費。
7. 確認報價單金額及內容，請簽章後回傳電子檔。
8. 本案之報價單回傳簽署後視為正式合約並支付50%訂金，交付製作檔案後30日需付清尾款。
9. 本報價單費用為專案優惠價，不可作為往後專案報價依據。"""

    # 公司資訊
    COMPANIES = {
        "魚游製作工作室": {
            "name": "魚游製作工作室",
            "default": True
        },
        "好歐映像工作室": {
            "name": "好歐映像工作室",
            "default": False
        }
    }

# HTML報價單處理模組
class QuoteGenerator:
    @staticmethod
    def generate_html_quote(client_name, project_name, project_type, shoot_date, shoot_hours, add_on_items, 
                          company_info=None, video_options=None):
        """生成HTML格式的報價單，支援完整的中文顯示與更專業的排版"""
        # 獲取當前專案詳情
        project_data = ProjectData.PROJECT_DETAILS[project_type]
        is_per_photo = project_data.get("per_photo", False)
        
        # 檢查是否提供小檔毛片
        provide_raw_files = False
        for item in add_on_items:
            if item['name'] == "提供小檔毛片":
                provide_raw_files = True
                break
        
        # 設定攝影師規格說明
        if project_type.startswith("平面拍攝"):
            if "商品拍攝(張計費)" in project_type:
                photographer_spec = "(1) 以張計費\n(2) 基本拍攝2張起\n(3) 適合電商產品主圖、廣告用商品照"
                if provide_raw_files:
                    photographer_spec += "\n(4) 提供小檔毛片(2MB/JPG)"
            elif "商品拍攝(時計費)" in project_type:
                photographer_spec = "(1) 以時計費\n(2) 基本出班為3小時\n(3) 適合多角度商品拍攝、社群內容使用"
                if provide_raw_files:
                    photographer_spec += "\n(4) 提供小檔毛片(2MB/JPG)"
            elif project_type == "平面拍攝-活動":
                photographer_spec = "(1) 以時計費\n(2) 基本出班為2小時\n(3) 提供活動照片"
                if provide_raw_files:
                    photographer_spec += "\n(4) 提供小檔毛片(2MB/JPG)"
            elif project_type == "平面拍攝-品牌形象":
                photographer_spec = "(1) 以時計費\n(2) 基本出班為4小時\n(3) 適合企業形象照、產品情境照"
                if provide_raw_files:
                    photographer_spec += "\n(4) 提供小檔毛片(2MB/JPG)"
            else:
                photographer_spec = "(1) 以時計費\n(2) 基本出班為2小時\n(3) 時間含30分鐘架設時間"
                if provide_raw_files:
                    photographer_spec += "\n(4) 提供小檔毛片(2MB/JPG)"
        else:
            photographer_spec = "(1) 以時計費\n(2) 基本出班為4小時\n(3) 時間含1小時前置架設\n(4) 包含基本剪輯及調色\n(5) 提供兩次修改機會"
        
        # 設置中文字體樣式與更現代的排版
        styles = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
            
            body {
                font-family: 'Noto Sans TC', Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #333;
                background-color: #f9f9f9;
            }
            .container {
                max-width: 800px;
                margin: 20px auto;
                padding: 40px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
                background-color: #fff;
                border-radius: 6px;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .logo {
                max-width: 150px;
                max-height: 80px;
            }
            h1 {
                text-align: center;
                color: #222;
                margin-bottom: 30px;
                font-weight: 700;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 15px;
            }
            .header-info {
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 20px;
            }
            .header-block {
                flex: 1;
            }
            .right-align {
                text-align: right;
            }
            .quote-id {
                color: #666;
                font-size: 0.95em;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
            }
            th, td {
                border: 1px solid #e0e0e0;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f7f7f7;
                font-weight: 500;
            }
            .amount {
                text-align: right;
            }
            .total-row {
                font-weight: 700;
                background-color: #f8f9fa;
            }
            .section-title {
                margin-top: 20px;
                font-weight: bold;
                background-color: #f8f9fa;
                padding: 8px 12px;
                border-left: 4px solid #4a86e8;
            }
            .remarks {
                font-size: 0.9em;
                margin-top: 30px;
                border-top: 1px solid #e0e0e0;
                padding-top: 20px;
                color: #555;
            }
            .signature {
                margin-top: 50px;
                text-align: center;
                padding-top: 30px;
                border-top: 1px dashed #e0e0e0;
            }
            .spec-text {
                white-space: pre-line;
                color: #555;
                font-size: 0.9em;
            }
            .category-title {
                background-color: #f0f0f0;
                font-weight: 700;
                color: #444;
            }
            .quote-footer {
                margin-top: 40px;
                text-align: center;
                font-size: 0.85em;
                color: #888;
                border-top: 1px solid #f0f0f0;
                padding-top: 20px;
            }
            .print-button {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1em;
                margin-top: 15px;
            }
            .print-button:hover {
                background-color: #3a76d8;
            }
            @media print {
                body {
                    font-size: 12pt;
                    background: none;
                }
                .no-print {
                    display: none;
                }
                .container {
                    border: none;
                    box-shadow: none;
                    padding: 0;
                }
                .remarks ol li {
                    margin-bottom: 8px;
                }
            }
        </style>
        """
        
        # 計算總金額
        hourly_rate = project_data["hourly_rate"]
        base_amount = hourly_rate * shoot_hours
        
        # 過濾掉小檔毛片項目(已顯示在攝影師規格中)
        filtered_items = []
        for item in add_on_items:
            if item['name'] != "提供小檔毛片":
                filtered_items.append(item)
        
        additional_amount = sum(item['amount'] for item in filtered_items)
        subtotal = base_amount + additional_amount
        tax = subtotal * CONFIG["TAX_RATE"]
        total = subtotal + tax
        
        # 分類項目
        # 預設排序順序
        order_items = [
            "攝影師",
            "平面攝助",
            "燈光師",
            "燈光助理",
            "燈光",
            "燈光設備",
            "美術",  # 改名為美術
            "美術道具費",
            "道具採買",
            "企劃費",
            "攝影棚",
            "車馬費"
        ]
        
        # 對項目進行排序
        sorted_items = []
        for name in order_items:
            for item in filtered_items:
                if item['name'] == name:
                    sorted_items.append(item)
        
        # 添加其他未在預設順序中的項目
        for item in filtered_items:
            if item['name'] not in order_items:
                sorted_items.append(item)
        
        # 生成報價單號 - 依照客戶名稱、專案類型和日期生成更有組織性的編號
        category_code = ""
        if project_type.startswith("平面拍攝"):
            category_code = "P"
        elif project_type.startswith("影像拍攝"):
            category_code = "V"
        else:
            category_code = "O"
            
        # 客戶名稱縮寫（取前兩個字）
        client_code = ""
        if client_name:
            client_code = client_name[:2]
        
        # 日期編碼
        date_code = datetime.datetime.now().strftime('%Y%m%d')
        
        # 序號（時分）
        sequence = datetime.datetime.now().strftime('%H%M')
        
        # 組合報價單號
        quote_number = f"Q{category_code}{client_code}{date_code}-{sequence}"
        
        # 處理公司資訊
        company_name = company_info.get("name", "專業攝影服務") if company_info else "專業攝影服務"
        
        # 建立HTML內容 - 注意：使用單引號代替雙引號，並將全形冒號改為半形冒號
        html = f'''
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>報價單_{client_name}_{datetime.datetime.now().strftime('%Y%m%d')}</title>
            {styles}
        </head>
        <body>
            <div class="container">
                <h1>{project_name or company_name}拍攝報價單</h1>
                
                <div class="header-info">
                    <div class="header-block">
                        <p><strong>客戶名稱:</strong>{client_name}</p>
                        <p><strong>製作方:</strong>{company_name}</p>
                        <p><strong>專案類型:</strong>{project_type}</p>
                        <p><strong>拍攝日期:</strong>{shoot_date.strftime('%Y-%m-%d') if shoot_date else '待定'}</p>
                    </div>
                    <div class="header-block right-align">
                        <p><strong>日期:</strong>{datetime.datetime.now().strftime('%Y-%m-%d')}</p>
                        <p><strong>報價單號:</strong><span class="quote-id">{quote_number}</span></p>
                        <p><strong>有效期限:</strong>{(datetime.datetime.now() + datetime.timedelta(days=28)).strftime('%Y-%m-%d')}</p>
                    </div>
                </div>
        '''
        
        # 表格開始
        html += f'''
                <table>
                    <thead>
                        <tr>
                            <th width="20%">品名</th>
                            <th width="40%">規格</th>
                            <th width="10%">單位</th>
                            <th width="15%">單價</th>
                            <th width="15%">金額</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 攝影師基本費用 -->
                        <tr>
                            <td>攝影師</td>
                            <td class="spec-text">{photographer_spec}</td>
                            <td>{shoot_hours}{("張" if is_per_photo else "小時")}</td>
                            <td class="amount">${hourly_rate:,}/{("張" if is_per_photo else "小時")}</td>
                            <td class="amount">${base_amount:,}</td>
                        </tr>
        '''
        
        # 添加所有項目（已排序）
        for item in sorted_items:
            unit = item.get('unit', '式')
            quantity = item['quantity']
            unit_display = f"{quantity}{unit}"
            
            # 處理實報實銷的情況
            price_display = "$" + f"{item['price']:,}" if not item.get('actual_expense', False) else "實報實銷"
            amount_display = "$" + f"{item['amount']:,}" if not item.get('actual_expense', False) else "實報實銷"
            
            # 修改spec，不在規格中顯示實報實銷
            spec_text = item['spec']
            if " (實報實銷)" in spec_text:
                spec_text = spec_text.replace(" (實報實銷)", "")
            
            html += f'''
                <tr>
                    <td>{item['name']}</td>
                    <td class="spec-text">{spec_text}</td>
                    <td>{unit_display}</td>
                    <td class="amount">{price_display}</td>
                    <td class="amount">{amount_display}</td>
                </tr>
            '''
        
        # 總計部分 - 單行字符串拼接
        html += '<tr class="total-row"><td colspan="4" class="amount">小計</td>'
        html += f'<td class="amount">${subtotal:,}</td></tr>'

        html += '<tr><td colspan="4" class="amount">稅金 ('
        html += f'{int(CONFIG["TAX_RATE"]*100)}%)</td>'
        html += f'<td class="amount">${tax:,}</td></tr>'
        
        # 最終總計行
        html += '<tr class="total-row"><td colspan="4" class="amount">總計 (含稅)</td>'
        html += f'<td class="amount">${total:,}</td></tr>'
        
        # 備註說明
        html += f'''
                </tbody>
                </table>
                
                <div class="remarks">
                    <h3>說明事項:</h3>
                    <ol>
                        <li>拍攝前三週需提供詳細拍攝內容企劃，如拍攝規格變動請立刻告知，並依新需求供新報價單。</li>
                        <li>拍攝需求如需購買一次性拍攝道具、美術陳設、協助購買道具、車馬費，費用另計。</li>
                        <li>以時計費方案，時間包含前置至結束之時間，前置時間約1-1.5hr，如拍攝遇用餐時間，需提供餐盒。</li>
                        <li>報價單有效期限為報價日期後四週。</li>
                        <li>報價金額皆未稅。</li>
                        <li>如於拍攝日前7日取消，需付總金額之30%製作費及已購買及租借之道具、器材費。</li>
                        <li>確認報價單金額及內容，請簽章後回傳電子檔。</li>
                        <li>本案之報價單回傳簽署後視為正式合約並支付50%訂金，交付製作檔案後30日需付清尾款。</li>
                        <li>本報價單費用為專案優惠價，不可作為往後專案報價依據。</li>
                    </ol>
                </div>
                
                <div class="signature">
                    <p>客戶簽章:_______________________</p>
                    <p>日期:_______________________</p>
                </div>
                
                <div class="quote-footer">
                    本報價單由{company_name}製作
                </div>
                
                <div class="no-print" style="margin-top: 40px; text-align: center;">
                    <p>(列印此頁面時，此區塊將不會顯示)</p>
                    <button class="print-button" onclick="window.print()">列印報價單</button>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html

    @staticmethod
    def get_html_download_link(html_string, filename="報價單.html"):
        """生成HTML檔案的下載連結"""
        b64 = base64.b64encode(html_string.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="download-button">下載HTML報價單</a>'
        return href

def display_summary(client_name, project_type, shoot_date, shoot_hours, add_on_items, current_project, discount_rate=1.0):
    """顯示報價單摘要"""
    st.subheader("📊 報價摘要", divider=True)
    
    # 檢查是否為張數計費
    is_per_photo = current_project.get("per_photo", False)
    
    # 計算基本費用
    hourly_rate = current_project.get("hourly_rate", 0)
    base_amount = hourly_rate * shoot_hours
    
    # 創建價格摘要DataFrame
    if is_per_photo:
        summary_data = [
            {"項目": "攝影師基本費用", "金額": base_amount, "說明": f"{shoot_hours}張 x ${hourly_rate:,}/張"}
        ]
    else:
        summary_data = [
            {"項目": "攝影師基本費用", "金額": base_amount, "說明": f"{shoot_hours}小時 x ${hourly_rate:,}/小時"}
        ]
    
    # 加購項目
    additional_amount = 0
    for item in add_on_items:
        # 檢查是否為提供小檔毛片（在攝影師規格中顯示，不單獨計費）
        if item['name'] == "提供小檔毛片":
            continue
            
        # 檢查是否為實報實銷項目
        if item.get('actual_expense', False):
            description = f"{item.get('unit', '')} (實報實銷)"
        else:
            description = f"{item['quantity']} {item.get('unit', '')} x ${item['price']:,}" if item['quantity'] > 1 else f"${item['price']:,}/{item.get('unit', '')}"
        
        summary_data.append({
            "項目": item['name'],
            "金額": item['amount'],
            "說明": description
        })
        additional_amount += item['amount']
    
    # 計算稅金和總額
    subtotal = base_amount + additional_amount
    
    # 應用折扣
    if discount_rate < 1.0:
        discount_amount = subtotal * (1 - discount_rate)
        subtotal_after_discount = subtotal - discount_amount
        
        # 添加折扣行
        summary_data.append({
            "項目": f"折扣 ({int((1-discount_rate)*100)}%折)",
            "金額": -discount_amount,
            "說明": f"優惠折扣"
        })
    else:
        subtotal_after_discount = subtotal
        discount_amount = 0
    
    tax = subtotal_after_discount * CONFIG["TAX_RATE"]
    total = subtotal_after_discount + tax
    
    # 增加小計、稅金和總計行
    summary_data.extend([
        {"項目": "小計", "金額": subtotal_after_discount, "說明": "折扣後金額" if discount_rate < 1.0 else "未稅金額"},
        {"項目": f"稅金 ({int(CONFIG['TAX_RATE']*100)}%)", "金額": tax, "說明": ""},
        {"項目": "總計", "金額": total, "說明": "含稅金額"}
    ])
    
    # 轉換為DataFrame並顯示
    df = pd.DataFrame(summary_data)
    
    # 格式化金額欄位
    df["金額"] = df["金額"].apply(lambda x: f"${x:,.0f}")
    
    # 使用Streamlit的資料表顯示
    st.dataframe(
        df,
        column_config={
            "項目": st.column_config.TextColumn("項目"),
            "金額": st.column_config.TextColumn("金額", width="medium"),
            "說明": st.column_config.TextColumn("說明")
        },
        hide_index=True,
        use_container_width=True
    )
    
    return total

def create_add_on_sections(project_type, project_name):
    """創建加購項目區域"""
    # 判斷是否為平面拍攝相關專案
    is_photography_project = project_type.startswith("平面拍攝")
    is_product_shoot = "商品拍攝" in project_type
    is_event_photography = project_type == "平面拍攝-活動"
    add_on_items = []
    
    # 查看項目是否需要企劃選項
    current_project = ProjectData.PROJECT_DETAILS.get(project_type, {})
    needs_planning = current_project.get("planning_options", False)
    discount_rate = 1.0  # 初始化折扣率
    
    # 自定義按鈕顏色風格
    button_style = """
    <style>
    .stTabs [data-baseweb="tab"] {
        background-color: #2c3e50;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a2c3d !important;
        border-top: 2px solid #3498db;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    # 使用標籤頁顯示不同類型的加購項目
    tabs = st.tabs([
        "📷 拍攝配置", 
        "🎨 美術道具",
        "✨ 後製服務", 
        "🏢 場地與交通", 
        "➕ 自訂項目",
        "🏷️ 折扣優惠"
    ])
    
    try:
        # Tab 1: 拍攝配置
        with tabs[0]:
            st.subheader("拍攝相關配置")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 平面攝助選項 - 修改為單價×人數的計算方式
                if is_photography_project:
                    item_name = "平面攝助"
                    item_config = ProjectData.ADD_ONS["拍攝相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    # 是否需要攝助
                    need_assistant = st.checkbox("需要攝助", key="need_assistant_checkbox")
                    
                    if need_assistant:
                        # 每位單價
                        assistant_price = st.number_input(
                            "每位攝助費用", 
                            min_value=0, 
                            step=500, 
                            value=2000, 
                            key="assistant_price", 
                            format="%d"
                        )
                        
                        assistant_count = st.number_input(
                            "攝助人數", 
                            min_value=1, 
                            max_value=4,
                            value=1, 
                            key="assistant_count", 
                            format="%d"
                        )
                        
                        if assistant_price > 0 and assistant_count > 0:
                            add_on_items.append({
                                'name': item_name,
                                'spec': item_config["spec"],
                                'quantity': assistant_count,
                                'unit': "位",
                                'price': assistant_price,
                                'amount': assistant_price * assistant_count
                            })
                
                # 燈光處理 - 針對活動或商品拍攝
                if is_event_photography or is_product_shoot:
                    item_name = "燈光"
                    item_config = ProjectData.ADD_ONS["拍攝相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    options = item_config["options"]
                    option_labels = [option["label"] for option in options]
                    
                    selected_index = st.selectbox(
                        f"選擇{item_name}",
                        range(len(option_labels)),
                        format_func=lambda i: option_labels[i],
                        key=f"addon_{item_name}"
                    )
                    
                    selected_option = options[selected_index]
                    selected_value = selected_option["value"]
                    
                    if selected_value > 0:
                        add_on_items.append({
                            'name': item_name,
                            'spec': item_config["spec"],
                            'quantity': 1,
                            'unit': "式",
                            'price': selected_value,
                            'amount': selected_value
                        })
                
                # 燈光師選項 - 不適用於活動或商品拍攝
                if not is_event_photography and not is_product_shoot:
                    item_name = "燈光師"
                    item_config = ProjectData.ADD_ONS["拍攝相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    options = item_config["options"]
                    option_labels = [option["label"] for option in options]
                    
                    selected_index = st.selectbox(
                        f"選擇{item_name}",
                        range(len(option_labels)),
                        format_func=lambda i: option_labels[i],
                        key=f"addon_{item_name}"
                    )
                    
                    selected_option = options[selected_index]
                    selected_value = selected_option["value"]
                    
                    if selected_value > 0:
                        add_on_items.append({
                            'name': item_name,
                            'spec': item_config["spec"],
                            'quantity': 1,
                            'unit': "位",
                            'price': selected_value,
                            'amount': selected_value
                        })
                
                # 美術人員選項 - 不適用於活動拍攝 - 已優化為總費用+人數方式
                if not is_event_photography:
                    item_name = "美術"  # 改名為美術
                    item_config = ProjectData.ADD_ONS["拍攝相關"]["美術"] # 使用項目中的"美術"
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    # 是否需要美術
                    need_art_personnel = st.checkbox("需要美術", key="need_art_personnel_checkbox")
                    
                    if need_art_personnel:
                        # 美術人員總費用
                        art_total_fee = st.number_input(
                            "美術人員總費用", 
                            min_value=0, 
                            step=1000, 
                            value=5000, 
                            key="art_total_fee", 
                            format="%d"
                        )
                        
                        art_personnel_count = st.number_input(
                            "美術人數", 
                            min_value=1, 
                            max_value=5,
                            value=1, 
                            key="art_personnel_count", 
                            format="%d"
                        )
                        
                        if art_total_fee > 0:
                            add_on_items.append({
                                'name': item_name,
                                'spec': f"{item_config['spec']} ({art_personnel_count}位美術人員)",
                                'quantity': 1,
                                'unit': "式",
                                'price': art_total_fee,
                                'amount': art_total_fee
                            })
            
            with col2:
                # 燈光助理選項 - 不適用於活動拍攝或商品拍攝
                if not is_event_photography and not is_product_shoot:
                    item_name = "燈光助理"
                    item_config = ProjectData.ADD_ONS["拍攝相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    # 是否需要燈光助理
                    need_light_assistant = st.checkbox("需要燈光助理", key="need_light_assistant_checkbox")
                    
                    if need_light_assistant:
                        # 每位單價
                        light_assistant_price = st.number_input(
                            "每位燈光助理費用", 
                            min_value=0, 
                            step=500, 
                            value=2000, 
                            key="light_assistant_price", 
                            format="%d"
                        )
                        
                        light_assistant_count = st.number_input(
                            "燈光助理人數", 
                            min_value=1, 
                            max_value=4,
                            value=1, 
                            key="light_assistant_count", 
                            format="%d"
                        )
                        
                        if light_assistant_price > 0 and light_assistant_count > 0:
                            add_on_items.append({
                                'name': item_name,
                                'spec': item_config["spec"],
                                'quantity': light_assistant_count,
                                'unit': "位",
                                'price': light_assistant_price,
                                'amount': light_assistant_price * light_assistant_count
                            })
                
                # 燈光設備選項 - 不適用於活動或商品拍攝
                if not is_event_photography and not is_product_shoot:
                    item_name = "燈光設備"
                    item_config = ProjectData.ADD_ONS["拍攝相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} 額外{item_name}")
                    
                    light_equipment_spec = st.text_input(
                        "燈光設備說明", 
                        key="light_equipment_spec",
                        help="詳細描述額外燈光設備需求"
                    )
                    light_equipment_price = st.number_input(
                        "燈光設備費用", 
                        min_value=0, 
                        step=1000, 
                        value=0, 
                        key="light_equipment_price", 
                        format="%d"
                    )
                    
                    if light_equipment_spec and light_equipment_price > 0:
                        add_on_items.append({
                            'name': item_name,
                            'spec': light_equipment_spec,
                            'quantity': 1,
                            'unit': "式",
                            'price': light_equipment_price,
                            'amount': light_equipment_price
                        })
        
        # Tab 2: 美術道具
        with tabs[1]:
            if not is_event_photography:
                st.subheader("美術與道具費用")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 美術道具費用
                    item_name = "美術道具費"
                    item_config = ProjectData.ADD_ONS["美術道具"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    art_spec = st.text_input(
                        "美術道具 (規格描述)", 
                        key="art_spec",
                        help="詳細描述所需的美術設計與道具內容"
                    )
                    art_price = st.number_input(
                        "美術道具費金額", 
                        min_value=0, 
                        step=1000, 
                        value=0, 
                        key="art_price", 
                        format="%d"
                    )
                    
                    # 實報實銷選項
                    art_actual_expense = st.checkbox(
                        "實報實銷",
                        key="art_actual_expense",
                        help="勾選此項表示美術道具費用為預估，實際將以實報實銷方式結算"
                    )
                    
                    if art_spec and (art_price > 0 or art_actual_expense):
                        add_on_items.append({
                            'name': '美術道具費',
                            'spec': art_spec + (" (實報實銷)" if art_actual_expense else ""),
                            'quantity': 1,
                            'unit': "式",
                            'price': art_price if not art_actual_expense else 0,
                            'amount': art_price if not art_actual_expense else 0,
                            'actual_expense': art_actual_expense
                        })
                    
                    # 企劃選項 - 根據專案類型顯示
                    if needs_planning:
                        item_name = "企劃費"
                        item_config = ProjectData.ADD_ONS["美術道具"][item_name]
                        icon = item_config.get("icon", "")
                        
                        st.markdown(f"##### {icon} {item_name}")
                        
                        planning_spec = st.text_input(
                            "拍攝企劃內容描述", 
                            key="planning_spec",
                            help="詳細描述企劃服務內容"
                        )
                        planning_price = st.number_input(
                            "企劃費金額", 
                            min_value=0, 
                            step=1000, 
                            value=0, 
                            key="planning_price", 
                            format="%d"
                        )
                        
                        if planning_spec and planning_price > 0:
                            add_on_items.append({
                                'name': '企劃費',
                                'spec': planning_spec,
                                'quantity': 1,
                                'unit': "式",
                                'price': planning_price,
                                'amount': planning_price
                            })
                
                with col2:
                    # 道具採買選項 - 簡化顯示
                    item_name = "道具採買"
                    item_config = ProjectData.ADD_ONS["美術道具"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    
                    options = item_config["options"]
                    option_labels = [option["label"] for option in options]
                    
                    selected_index = st.selectbox(
                        f"選擇{item_name}費用",
                        range(len(option_labels)),
                        format_func=lambda i: option_labels[i],
                        key=f"addon_{item_name}"
                    )
                    
                    selected_option = options[selected_index]
                    selected_value = selected_option["value"]
                    
                    if selected_value > 0:
                        add_on_items.append({
                            'name': item_name,
                            'spec': item_config["spec"],
                            'quantity': 1,
                            'unit': item_config.get("unit", "式"),
                            'price': selected_value,
                            'amount': selected_value
                        })
            else:
                st.info("活動拍攝專案通常不需要美術道具，此區塊已隱藏")
        
        # Tab 3: 後製服務
        with tabs[2]:
            st.subheader("後製項目選擇")
            
            # 先處理小檔毛片選項 - 平面拍攝適用
            if is_photography_project:
                item_name = "提供小檔毛片"
                item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                icon = item_config.get("icon", "")
                
                st.markdown(f"##### {icon} {item_name}")
                include_raw_files = st.checkbox(
                    "提供小檔毛片(2MB/JPG)",
                    key="addon_raw_files",
                    help="提供小檔毛片可用於快速瀏覽或社群媒體參考"
                )
                
                if include_raw_files:
                    add_on_items.append({
                        'name': item_name,
                        'spec': item_config["spec"],
                        'quantity': 1,
                        'unit': "項",
                        'price': 0,
                        'amount': 0
                    })
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 網路用精修選項
                if is_photography_project:
                    item_name = "網路用精修"
                    item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    include_web_retouch = st.checkbox(
                        f"網路用精修 ${item_config['price']}/張",
                        key="addon_web_retouch",
                        help="適合網路發布使用的基礎修圖服務"
                    )
                    
                    if include_web_retouch:
                        quantity = st.number_input(
                            "張數",
                            min_value=1,
                            value=5,
                            key=f"addon_{item_name}_quantity"
                        )
                        
                        add_on_items.append({
                            'name': item_name,
                            'spec': item_config["spec"],
                            'quantity': quantity,
                            'unit': "張",
                            'price': item_config["price"],
                            'amount': item_config["price"] * quantity
                        })
                
                # 大圖精修選項
                if is_photography_project:
                    item_name = "大圖精修"
                    item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    include_large_retouch = st.checkbox(
                        f"大圖精修 ${item_config['price']}/張",
                        key="addon_large_retouch",
                        help="適合廣告大圖使用的高階修圖服務"
                    )
                    
                    if include_large_retouch:
                        quantity = st.number_input(
                            "張數",
                            min_value=1,
                            value=3,
                            key=f"addon_{item_name}_quantity"
                        )
                        
                        add_on_items.append({
                            'name': item_name,
                            'spec': item_config["spec"],
                            'quantity': quantity,
                            'unit': "張",
                            'price': item_config["price"],
                            'amount': item_config["price"] * quantity
                        })
                
                # 優化去背選項 - 不適用於活動拍攝
                if is_photography_project and not is_event_photography:
                    item_name = "去背"
                    item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    include_background_removal = st.checkbox(
                        "去背服務",
                        key="addon_background_removal",
                        help="產品或人物去背服務"
                    )
                    
                    if include_background_removal:
                        # 去背類型選擇
                        bg_removal_type = st.radio(
                            "去背類型",
                            options=["商品去背", "人像去背"],
                            key="bg_removal_type"
                        )
                        
                        # 根據不同去背類型設定不同預設價格
                        default_price = 300 if bg_removal_type == "商品去背" else 2500
                        price_max = 1000 if bg_removal_type == "商品去背" else 5000
                        price_step = 100 if bg_removal_type == "商品去背" else 500
                        
                        col_bg1, col_bg2, col_bg3 = st.columns([2, 1, 1])
                        with col_bg1:
                            bg_quantity = st.number_input(
                                "張數",
                                min_value=1,
                                value=3,
                                key="addon_bg_removal_quantity"
                            )
                        
                        with col_bg2:
                            bg_price = st.number_input(
                                "單價",
                                min_value=100,
                                max_value=price_max,
                                value=default_price,
                                step=price_step,
                                key="addon_bg_removal_price"
                            )
                        
                        with col_bg3:
                            st.write("&nbsp;")
                            st.write("&nbsp;")
                            price_str = f"${bg_price}/張"
                            st.write(price_str)
                        
                        # 簡化去背規格描述
                        if bg_removal_type == "商品去背":
                            bg_spec = "商品去背服務"
                        else:
                            bg_spec = "人像去背服務"
                        
                        add_on_items.append({
                            'name': item_name,
                            'spec': bg_spec,
                            'quantity': bg_quantity,
                            'unit': "張",
                            'price': bg_price,
                            'amount': bg_price * bg_quantity
                        })
            
            with col2:
                # 優化調光調色選項
                item_name = "調光調色"
                item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                icon = item_config.get("icon", "")
                
                st.markdown(f"##### {icon} {item_name}")
                
                # 先勾選是否需要調光調色
                need_color_grading = st.checkbox(
                    "需要調光調色",
                    key="need_color_grading_checkbox",
                    help="全照片調光調色，提供6MB JPG檔"
                )
                
                if need_color_grading:
                    # 選擇時數方案
                    color_grading_option = st.radio(
                        "調光調色方案",
                        options=["標準方案 $3,500 (4小時內)", "進階方案 $7,000 (8小時內)"],
                        key="color_grading_option"
                    )
                    
                    # 根據選擇設定價格
                    color_grading_price = 3500 if "標準方案" in color_grading_option else 7000
                    color_grading_spec = "全照片調光調色，提供6MB JPG檔 (4小時內)" if "標準方案" in color_grading_option else "全照片調光調色，提供6MB JPG檔 (8小時內)"
                    
                    add_on_items.append({
                        'name': item_name,
                        'spec': color_grading_spec,
                        'quantity': 1,
                        'unit': "式",
                        'price': color_grading_price,
                        'amount': color_grading_price
                    })
                
                # 現場出圖選項 - 僅適用於活動拍攝
                if is_event_photography:
                    item_name = "現場出圖"
                    item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                    icon = item_config.get("icon", "")
                    
                    st.markdown(f"##### {icon} {item_name}")
                    include_onsite_output = st.checkbox(
                        "現場出圖服務",
                        key="addon_onsite_output",
                        help="活動現場即時出圖服務"
                    )
                    
                    if include_onsite_output:
                        onsite_output_spec = st.text_input(
                            "現場出圖服務說明",
                            key="onsite_output_spec",
                            help="說明現場出圖服務的細節"
                        )
                        onsite_output_price = st.number_input(
                            "現場出圖費用", 
                            min_value=0, 
                            step=1000, 
                            value=0, 
                            key="onsite_output_price", 
                            format="%d"
                        )
                        onsite_output_qty = st.number_input(
                            "出圖張數", 
                            min_value=0, 
                            step=10, 
                            value=0, 
                            key="onsite_output_qty"
                        )
                        
                        if onsite_output_spec and onsite_output_price > 0:
                            add_on_items.append({
                                'name': item_name,
                                'spec': f"{onsite_output_spec} ({onsite_output_qty}張)",
                                'quantity': 1,
                                'unit': "式",
                                'price': onsite_output_price,
                                'amount': onsite_output_price
                            })
                
                # 新增急件處理選項
                item_name = "急件處理"
                item_config = ProjectData.ADD_ONS["後製相關"][item_name]
                icon = item_config.get("icon", "")
                
                st.markdown(f"##### {icon} {item_name}")
                include_rush_fee = st.checkbox(
                    "急件處理費",
                    key="addon_rush_fee",
                    help="加急處理，縮短交付時間"
                )
                
                if include_rush_fee:
                    rush_fee_spec = st.text_input(
                        "急件處理說明",
                        key="rush_fee_spec",
                        help="說明急件處理的細節，如縮短至多少時間內交付"
                    )
                    rush_fee_price = st.number_input(
                        "急件處理費用", 
                        min_value=0, 
                        step=500, 
                        value=0, 
                        key="rush_fee_price", 
                        format="%d"
                    )
                    
                    if rush_fee_spec and rush_fee_price > 0:
                        add_on_items.append({
                            'name': item_name,
                            'spec': rush_fee_spec,
                            'quantity': 1,
                            'unit': "式",
                            'price': rush_fee_price,
                            'amount': rush_fee_price
                        })
        
        # Tab 4: 場地與交通
        with tabs[3]:
            st.subheader("場地與交通費用")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 攝影棚選項
                item_name = "攝影棚"
                item_config = ProjectData.ADD_ONS["場地相關"][item_name]
                icon = item_config.get("icon", "")
                
                st.markdown(f"##### {icon} {item_name}")
                include_studio = st.checkbox(
                    "租用攝影棚",
                    key="addon_studio",
                    help="使用專業攝影棚進行拍攝"
                )
                
                if include_studio:
                    studio_hours = st.selectbox(
                        "攝影棚時數",
                        options=item_config["hours_options"],
                        key=f"addon_{item_name}_hours"
                    )
                    
                    price_options = item_config["price_options"]
                    price_labels = [option["label"] for option in price_options]
                    
                    selected_price_index = st.selectbox(
                        "攝影棚費率",
                        range(len(price_labels)),
                        format_func=lambda i: price_labels[i],
                        key=f"addon_{item_name}_price"
                    )
                    
                    selected_price_option = price_options[selected_price_index]
                    studio_price = selected_price_option["value"]
                    
                    add_on_items.append({
                        'name': item_name,
                        'spec': f"攝影棚租借 {price_labels[selected_price_index]}，共{studio_hours}小時",
                        'quantity': studio_hours,
                        'unit': "小時",
                        'price': studio_price,
                        'amount': studio_price * studio_hours
                    })
            
            with col2:
                # 車馬費選項 - 修改為需先勾選
                item_name = "車馬費"
                item_config = ProjectData.ADD_ONS["交通相關"][item_name]
                icon = item_config.get("icon", "")
                
                st.markdown(f"##### {icon} {item_name}")
                include_transportation = st.checkbox(
                    "加收車馬費",
                    key="addon_transportation",
                    help="加收交通車馬費"
                )
                
                if include_transportation:
                    options = item_config["options"]
                    option_labels = [option["label"] for option in options]
                    
                    selected_index = st.selectbox(
                        "車馬費金額",
                        range(len(option_labels)),
                        format_func=lambda i: option_labels[i],
                        key=f"addon_{item_name}"
                    )
                    
                    selected_option = options[selected_index]
                    selected_value = selected_option["value"]
                    
                    add_on_items.append({
                        'name': item_name,
                        'spec': item_config["spec"],
                        'quantity': 1,
                        'unit': "式",
                        'price': selected_value,
                        'amount': selected_value
                    })
        
        # Tab 5: 自訂項目
        with tabs[4]:
            st.subheader("自訂加購項目")
            
            custom_item_count = st.number_input(
                "自訂項目數量", 
                min_value=0, 
                max_value=5, 
                value=0,
                step=1
            )
            
            if custom_item_count > 0:
                for i in range(custom_item_count):
                    st.markdown(f"##### 自訂項目 {i+1}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        custom_name = st.text_input("項目名稱", key=f"custom_name_{i}")
                        custom_price = st.number_input("單價", min_value=0, step=100, key=f"custom_price_{i}")
                    
                    with col2:
                        custom_spec = st.text_input("規格描述", key=f"custom_spec_{i}")
                        custom_quantity = st.number_input("數量", min_value=0, value=1, key=f"custom_quantity_{i}")
                        custom_unit = st.text_input("單位", value="式", key=f"custom_unit_{i}")
                    
                    if custom_name and custom_price > 0 and custom_quantity > 0:
                        custom_amount = custom_price * custom_quantity
                        add_on_items.append({
                            'name': custom_name,
                            'spec': custom_spec,
                            'quantity': custom_quantity,
                            'unit': custom_unit,
                            'price': custom_price,
                            'amount': custom_amount
                        })
        
        # Tab 6: 優惠選項
        with tabs[5]:
            st.subheader("專案優惠")
            
            # 折扣選項
            item_name = "折扣"
            item_config = ProjectData.ADD_ONS["優惠"][item_name]
            icon = item_config.get("icon", "")
            
            st.markdown(f"##### {icon} 專案折扣")
            
            options = item_config["options"]
            option_labels = [option["label"] for option in options]
            
            selected_index = st.selectbox(
                "選擇折扣方案",
                range(len(option_labels)),
                format_func=lambda i: option_labels[i],
                key=f"addon_{item_name}"
            )
            
            selected_option = options[selected_index]
            discount_rate = selected_option["value"]
            
            if discount_rate < 1.0:
                st.info(f"已套用 {int((1-discount_rate)*100)}% 折扣")
    
    except Exception as e:
        st.error(f"設定表單時發生錯誤: {str(e)}")
    
    return add_on_items, discount_rate

def display_project_info(project_type):
    """顯示專案詳細資訊"""
    current_project = ProjectData.PROJECT_DETAILS.get(project_type, {})
    st.info(f"### 專案說明\n{current_project.get('description', '無說明')}")

def create_video_options_section(current_project):
    """創建影片選項區域"""
    video_options = {}
    if current_project.get("video_options", False):
        st.subheader("🎬 影片規格")
        col1, col2 = st.columns(2)
        with col1:
            video_length_options = current_project.get("video_length_options", [])
            if video_length_options:
                video_options["video_length"] = st.selectbox(
                    "影片長度", 
                    video_length_options,
                    help="選擇最終輸出的影片長度"
                )
        with col2:
            orientation_options = current_project.get("orientation_options", [])
            if orientation_options:
                video_options["orientation"] = st.selectbox(
                    "影片方向", 
                    orientation_options,
                    help="選擇影片的畫面比例方向"
                )
    return video_options

def get_company_options():
    """取得公司選項資訊"""
    companies = ProjectData.COMPANIES
    company_options = list(companies.keys())
    default_index = next((i for i, name in enumerate(company_options) 
                         if companies[name].get("default", False)), 0)
    return company_options, default_index

# 主程式
def main():
    # 設置頁面
    st.set_page_config(
        page_title=CONFIG["APP_TITLE"],
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自訂CSS
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .download-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #1E3A8A;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            text-align: center;
            margin: 10px 0;
        }
        .download-button:hover {
            background-color: #172B6A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 0.9rem;
        }
        .st-emotion-cache-1inwz65 {
            border-color: #f0f0f0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title('📸 專業攝影報價單生成系統')
    
    # 公司選擇 - 簡化設計
    company_options, default_company_index = get_company_options()
    selected_company = st.sidebar.selectbox(
        "選擇工作室",
        options=company_options,
        index=default_company_index
    )
    company_info = ProjectData.COMPANIES.get(selected_company)
    
    # 基本資訊
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input('👤 客戶名稱')
        project_name = st.text_input('📝 專案名稱')
    
    with col2:
        # 選擇專案類型
        categories = {}
        for key, value in ProjectData.PROJECT_DETAILS.items():
            category = value.get("category", "其他")
            if category not in categories:
                categories[category] = []
            categories[category].append(key)
        
        project_category = st.selectbox('📝 服務類別', options=list(categories.keys()))
        project_type = st.selectbox('📸 專案類型', options=categories[project_category])
    
    # 拍攝日期與時數
    col3, col4 = st.columns(2)
    
    with col3:
        shoot_date = st.date_input(
            "📅 拍攝日期", 
            value=None,
            min_value=datetime.datetime.now().date(),
            format="YYYY-MM-DD"
        )
    
    with col4:
        # 專案詳情
        current_project = ProjectData.PROJECT_DETAILS.get(project_type, {})
        min_hours = current_project.get("min_hours", 2)
        is_per_photo = current_project.get("per_photo", False)
        
        if is_per_photo:
            shoot_hours = st.number_input(
                '📷 拍攝張數', 
                min_value=min_hours, 
                value=min_hours,
                help=f"最少拍攝張數: {min_hours}張"
            )
            hourly_rate = current_project.get("hourly_rate", 0)
            base_amount = hourly_rate * shoot_hours
            st.info(f"🔢 基本費用: {shoot_hours}張 x ${hourly_rate:,}/張 = **${base_amount:,}**")
        else:
            shoot_hours = st.number_input(
                '⏱️ 拍攝時數 (小時)', 
                min_value=min_hours, 
                value=max(CONFIG["DEFAULT_HOURS"], min_hours),
                help=f"最少預約時數: {min_hours}小時"
            )
            hourly_rate = current_project.get("hourly_rate", 0)
            base_amount = hourly_rate * shoot_hours
            st.info(f"🔢 基本費用: {shoot_hours}小時 x ${hourly_rate:,}/小時 = **${base_amount:,}**")
    
    # 顯示專案說明
    display_project_info(project_type)
    
    # 影片選項
    video_options = create_video_options_section(current_project)
    
    # 加購項目
    add_on_items, discount_rate = create_add_on_sections(project_type, project_name)
    
    # 報價摘要
    total_amount = display_summary(client_name, project_type, shoot_date, shoot_hours, add_on_items, current_project, discount_rate)
    
    # 生成報價單
    st.divider()
    quote_col1, quote_col2 = st.columns([1, 2])
    
    with quote_col1:
        st.subheader("📄 生成正式報價單")
        st.info("報價單將以HTML格式生成，可直接列印為PDF")
        generate_button = st.button("產生報價單", use_container_width=True, type="primary")
        
        if generate_button:
            if not client_name:
                st.error("⚠️ 請輸入客戶名稱後再生成報價單")
            elif shoot_hours <= 0:
                st.error("⚠️ 拍攝時數必須大於0")
            else:
                with st.spinner("⏳ 正在生成報價單..."):
                    html_content = QuoteGenerator.generate_html_quote(
                        client_name, 
                        project_name,
                        project_type, 
                        shoot_date, 
                        shoot_hours, 
                        add_on_items,
                        company_info,
                        video_options
                    )
                    
                    st.success('✅ 報價單已生成！')
                    st.markdown(
                        QuoteGenerator.get_html_download_link(
                            html_content, 
                            f"報價單_{client_name}_{datetime.datetime.now().strftime('%Y%m%d')}.html"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    # 也提供一個使用PDF檔案的選項
                    st.info("""
                    **如何使用HTML報價單:**
                    1. 點擊上方連結下載HTML檔案
                    2. 用瀏覽器打開該檔案
                    3. 點擊頁面底部的「列印報價單」按鈕，或使用瀏覽器的列印功能（Ctrl+P或⌘+P）
                    4. 選擇「另存為PDF」將其儲存為PDF檔案
                    
                    此方式可保留所有格式，並方便您以電子郵件發送給客戶。
                    """)
    
    with quote_col2:
        # 預覽信息卡片
        if client_name and project_type:
            st.subheader("👁️ 報價單預覽")
            
            # 使用卡片風格顯示預覽
            preview_cols = st.columns(2)
            
            with preview_cols[0]:
                st.markdown(f"""
                **基本資訊:**
                * 客戶名稱: {client_name}
                * 製作方: {company_info.get('name', selected_company)}
                * 專案類型: {project_type}
                * 拍攝日期: {shoot_date.strftime('%Y-%m-%d') if shoot_date else '待定'}
                * 拍攝{("張數" if is_per_photo else "時數")}: {shoot_hours} {("張" if is_per_photo else "小時")}
                """)
            
            with preview_cols[1]:
                unit = "張" if is_per_photo else "小時"
                
                discount_info = f"（含{int((1-discount_rate)*100)}%折扣）" if discount_rate < 1.0 else ""
                
                st.markdown(f"""
                **預計費用:**
                * 基本攝影費: ${current_project['hourly_rate'] * shoot_hours:,} ({shoot_hours}{unit} x ${current_project['hourly_rate']:,}/{unit})
                * 加購項目數: {len(add_on_items)} 項
                * 總計金額: **${total_amount:,}** {discount_info}(含稅)
                """)
            
            # 顯示報價單簡要說明
            st.info(f"""
            本報價單在產生後將包含所有詳細費用明細、交付規格說明、付款條件等資訊。
            報價單有效期: {(datetime.datetime.now() + datetime.timedelta(days=28)).strftime('%Y-%m-%d')}
            發送公司: {company_info.get('name', selected_company)}
            """)
            
            # 如果有影片選項，顯示額外資訊
            if video_options:
                st.success(f"""
                **影片規格:**
                * 影片長度: {video_options.get('video_length', '未指定')}
                * 顯示方向: {video_options.get('orientation', '未指定')}
                """)

if __name__ == "__main__":
    main()

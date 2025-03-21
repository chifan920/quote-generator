import streamlit as st
import datetime
import os
import tempfile
import base64
from pathlib import Path

# 常數定義
TAX_RATE = 0.05
DEFAULT_HOURS = 3

# 台北攝影師報價行情及項目規格
project_details = {
    "平面拍攝-活動": {
        "hourly_rate": 3000,
        "video_options": False,
    },
    "平面拍攝-品牌形象": {
        "hourly_rate": 3500,
        "video_options": False,
    },
    "平面拍攝-廣告代言": {
        "hourly_rate": 6000,
        "video_options": False,
    },
    "影像拍攝-短影音": {
        "hourly_rate": 15000,
        "video_options": True,
        "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
        "orientation_options": ['直式', '橫式'],
    },
    "影像拍攝-訪談": {
        "hourly_rate": 12000,
        "video_options": True,
        "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
        "orientation_options": ['直式', '橫式'],
    },
    "影像拍攝-品牌形象": {
        "hourly_rate": 15000,
        "video_options": True,
        "video_length_options": ['15s', '30s', '60s', '90s', '180s'],
        "orientation_options": ['直式', '橫式'],
    }
}

# 平面攝影加購品項選項 - 已更新
photography_add_ons = {
    # 拍攝相關項目
    "拍攝相關": {
        "平面攝助": {
            "type": "dropdown",
            "options": [
                {"label": "不加購", "value": 0},
                {"label": "一位攝助 $2,000", "value": 2000},
                {"label": "兩位攝助 $4,000", "value": 4000}
            ],
            "spec": "協助拍攝"
        },
        "燈光助理": {
            "type": "dropdown",
            "options": [
                {"label": "不加購", "value": 0},
                {"label": "一位燈光助理 $2,000", "value": 2000},
                {"label": "兩位燈光助理 $4,000", "value": 4000}
            ],
            "spec": "協助燈光設置"
        },
        "燈光設備": {
            "type": "dropdown",
            "options": [
                {"label": "不加購", "value": 0},
                {"label": "基本燈光 $4,000", "value": 4000},
                {"label": "進階燈光 $8,000", "value": 8000},
                {"label": "專業燈光 $15,000", "value": 15000}
            ],
            "spec": "燈光設備"
        },
        "美術費": {
            "type": "fixed",
            "description": "美術設計與佈置費用",
            "unit": "一式"
        },
        "道具費": {
            "type": "fixed",
            "description": "拍攝道具費用",
            "unit": "一式"
        }
    },
    
    # 後製相關項目
    "後製相關": {
        "網路用精修": {
            "type": "with_quantity",
            "price": 1000,
            "description": "網路用精修 $1,000/張",
            "spec": "網路使用精修"
        },
        "大圖精修": {
            "type": "with_quantity",
            "price": 2500,
            "description": "大圖精修 $2,500/張",
            "spec": "(1)修圖範圍: 皮膚修飾、身形美化、調光調色\n(不包含：商品電修/合成、人像合成、去背、服裝調整）\n(2)人像去背 +$2,500/張"
        },
        "調光調色": {
            "type": "fixed",
            "description": "全照片調光調色",
            "unit": "一式",
            "price": 6000,
            "spec": "全照片調光調色，提供6MB JPG檔"
        }
    },
    
    # 場地相關項目
    "場地相關": {
        "攝影棚": {
            "type": "with_hours",
            "price": 1000,
            "description": "攝影棚 $1,000/小時",
            "spec": "【安宅六號】攝影棚\n新北市三重區重安街132號8樓\n攝影棚原價$1,800，攝影師自棚優惠"
        }
    },
    
    # 交通相關項目
    "交通相關": {
        "車馬費": {
            "type": "dropdown",
            "options": [
                {"label": "不加購", "value": 0},
                {"label": "基本車馬費 $500", "value": 500},
                {"label": "市區車馬費 $1,000", "value": 1000},
                {"label": "郊區車馬費 $1,500", "value": 1500},
                {"label": "遠程車馬費 $2,000", "value": 2000}
            ],
            "spec": "交通與運輸費用"
        }
    }
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

def generate_html_quote(client_name, project_type, shoot_hours, add_on_items, video_options=None):
    """
    生成HTML格式的報價單，支援完整的中文顯示
    """
    # 設置中文字體樣式
    styles = """
    <style>
        body {
            font-family: Arial, "Microsoft JhengHei", "Microsoft YaHei", "SimHei", sans-serif;
            margin: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .header-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .header-block {
            flex: 1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .amount {
            text-align: right;
        }
        .total-row {
            font-weight: bold;
            background-color: #ffffcc;
        }
        .section-title {
            margin-top: 20px;
            font-weight: bold;
            background-color: #f8f9fa;
            padding: 5px;
        }
        .remarks {
            font-size: 0.9em;
            margin-top: 30px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }
        .signature {
            margin-top: 40px;
            text-align: center;
        }
        .spec-text {
            white-space: pre-line;
        }
        @media print {
            body {
                font-size: 12pt;
            }
            .no-print {
                display: none;
            }
            .container {
                border: none;
            }
        }
    </style>
    """
    
    # 計算總金額
    hourly_rate = project_details[project_type]["hourly_rate"]
    base_amount = hourly_rate * shoot_hours
    additional_amount = sum(item['amount'] for item in add_on_items)
    subtotal = base_amount + additional_amount
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    
    # 分類項目
    shoot_items = [item for item in add_on_items if item['name'] in ['平面攝助', '燈光助理', '燈光設備', '美術費', '道具費']]
    post_items = [item for item in add_on_items if item['name'] in ['網路用精修', '大圖精修', '調光調色']]
    venue_items = [item for item in add_on_items if item['name'] in ['攝影棚']]
    transport_items = [item for item in add_on_items if item['name'] in ['車馬費']]
    other_items = [item for item in add_on_items if item not in shoot_items and item not in post_items 
                   and item not in venue_items and item not in transport_items]
    
    # 影片選項
    video_spec = ""
    if video_options:
        video_length = video_options.get("video_length", "")
        orientation = video_options.get("orientation", "")
        if video_length and orientation:
            video_spec = f"{video_length}，{orientation}"
    
    # 設定攝影師規格說明
    photographer_spec = ""
    if project_type.startswith("平面拍攝-活動"):
        photographer_spec = "(1) 以時計費\n(2) 基本出班為2小時\n(4) 拍攝毛片小檔可提供"
    else:
        photographer_spec = "(1) 以時計費\n(2) 基本出班為4小時\n(3) 時間含1小時前置架設\n(4) 拍攝毛片小檔可提供"
    
    # 建立HTML內容
    html = f"""
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
            <h1>報價單</h1>
            
            <div class="header-info">
                <div class="header-block">
                    <p><strong>客戶名稱：</strong>{client_name}</p>
                    <p><strong>專案類型：</strong>{project_type}</p>
                </div>
                <div class="header-block">
                    <p><strong>日期：</strong>{datetime.datetime.now().strftime('%Y-%m-%d')}</p>
                    <p><strong>報價單號：</strong>Q{datetime.datetime.now().strftime('%Y%m%d%H%M')}</p>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th width="20%">品名</th>
                        <th width="40%">規格</th>
                        <th width="10%">數量</th>
                        <th width="15%">單價</th>
                        <th width="15%">金額</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- 攝影師基本費用 -->
                    <tr>
                        <td>攝影師</td>
                        <td class="spec-text">{photographer_spec}</td>
                        <td>{shoot_hours}</td>
                        <td class="amount">${hourly_rate:,}</td>
                        <td class="amount">${base_amount:,}</td>
                    </tr>
    """
    
    # 所有加購項目 (不顯示分類標題)
    all_items = shoot_items + post_items + venue_items + transport_items + other_items
    for item in all_items:
        quantity_display = item['quantity']
        if item['name'] in ['美術費', '道具費', '調光調色']:
            quantity_display = "一式"
        
        html += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td class="spec-text">{item['spec']}</td>
                        <td>{quantity_display}</td>
                        <td class="amount">${item['price']:,}</td>
                        <td class="amount">${item['amount']:,}</td>
                    </tr>
        """
    
    # 總計部分
    html += f"""
                    <tr class="total-row">
                        <td colspan="4" class="amount">小計</td>
                        <td class="amount">${subtotal:,}</td>
                    </tr>
                    <tr>
                        <td colspan="4" class="amount">稅金 ({int(TAX_RATE*100)}%)</td>
                        <td class="amount">${tax:,}</td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="4" class="amount">總計 (含稅)</td>
                        <td class="amount">${total:,}</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="remarks">
                <h3>說明事項：</h3>
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
                <p>客戶簽章：_______________________</p>
                <p>日期：_______________________</p>
            </div>
            
            <div class="no-print" style="margin-top: 40px; text-align: center;">
                <p>(列印此頁面時，系統訊息將不會顯示)</p>
                <p><button onclick="window.print()">列印報價單</button></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def get_html_download_link(html_string, filename="報價單.html"):
    """生成HTML檔案的下載連結"""
    
    # 將HTML編碼為下載鏈接
    b64 = base64.b64encode(html_string.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">下載HTML報價單</a>'
    return href

# 儲存自訂項目
def process_custom_item(name, spec, price, quantity=1, unit=None):
    """處理自訂項目並返回項目字典"""
    if price <= 0:
        return None
    
    # 處理單位顯示
    display_spec = spec
    if unit == "一式":
        display_spec = f"{spec} (一式)"
        quantity = 1  # 強制數量為1
    
    return {
        'name': name,
        'spec': display_spec,
        'quantity': quantity,
        'price': price,
        'amount': price * quantity
    }

# Streamlit 主應用
def main():
    """Streamlit應用主函數"""
    st.set_page_config(page_title="攝影師報價單生成系統", layout="wide")
    st.title('自動化報價單生成系統')
    
    # 側邊欄的基本信息
    with st.sidebar:
        st.subheader("基本信息")
        client_name = st.text_input('客戶名稱')
        project_type = st.selectbox('專案類型', list(project_details.keys()))
        shoot_hours = st.number_input('拍攝時數 (小時)', min_value=1, value=DEFAULT_HOURS)
    
    # 獲取當前選擇專案的詳情
    current_project = project_details.get(project_type, {})
    
    # 初始化加購項目列表
    add_on_items = []
    
    # 條件顯示影片選項
    video_options = {}
    if current_project.get("video_options", False):
        st.subheader("影片選項")
        col1, col2 = st.columns(2)
        
        with col1:
            video_length_options = current_project.get("video_length_options", [])
            if video_length_options:
                video_options["video_length"] = st.selectbox("選擇影片長度", video_length_options)
        
        with col2:
            orientation_options = current_project.get("orientation_options", [])
            if orientation_options:
                video_options["orientation"] = st.selectbox("選擇影片方向", orientation_options)
    
    # 判斷是否為平面拍攝相關專案
    is_photography_project = project_type.startswith("平面拍攝")
    
    # 拍攝相關加購項目
    st.subheader("拍攝相關加購項目")
    shoot_cols = st.columns(2)
    
    with shoot_cols[0]:
        # 處理平面攝助選項
        if is_photography_project:
            item_name = "平面攝助"
            item_config = photography_add_ons["拍攝相關"][item_name]
            options = item_config["options"]
            option_labels = [option["label"] for option in options]
            
            selected_index = st.selectbox(
                f"{item_name}",
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
                    'price': selected_value,
                    'amount': selected_value
                })
            
            # 燈光助理選項
            if is_photography_project:
                item_name = "燈光助理"
                item_config = photography_add_ons["拍攝相關"][item_name]
                options = item_config["options"]
                option_labels = [option["label"] for option in options]
                
                selected_index = st.selectbox(
                    f"{item_name}",
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
                        'price': selected_value,
                        'amount': selected_value
                    })
        
        # 美術費用
        st.subheader("美術費用")
        art_spec = st.text_input("美術設計與佈置 (規格描述)", key="art_spec")
        art_price = st.number_input("美術費金額", min_value=0, step=1000, value=0, 
                                  key="art_price", format="%d")
        
        if art_spec and art_price > 0:
            add_on_items.append({
                'name': '美術費',
                'spec': art_spec,
                'quantity': 1,
                'price': art_price,
                'amount': art_price
            })
    
    with shoot_cols[1]:
        # 燈光設備選項
        if is_photography_project:
            item_name = "燈光設備"
            item_config = photography_add_ons["拍攝相關"][item_name]
            options = item_config["options"]
            option_labels = [option["label"] for option in options]
            
            selected_index = st.selectbox(
                f"{item_name}",
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
                    'price': selected_value,
                    'amount': selected_value
                })
        
        # 道具費用
        st.subheader("道具費用")
        prop_spec = st.text_input("道具費 (規格描述)", key="prop_spec")
        prop_price = st.number_input("道具費金額", min_value=0, step=1000, value=0, 
                                   key="prop_price", format="%d")
        
        if prop_spec and prop_price > 0:
            add_on_items.append({
                'name': '道具費',
                'spec': prop_spec,
                'quantity': 1,
                'price': prop_price,
                'amount': prop_price
            })
    
    # 車馬費
    st.subheader("交通費用")
    travel_spec = st.text_input("車馬費 (規格描述)", key="travel_spec")
    travel_price = st.number_input("車馬費金額", min_value=0, step=100, key="travel_price")
    
    if travel_spec and travel_price > 0:
        add_on_items.append({
            'name': '車馬費',
            'spec': travel_spec,
            'quantity': 1,
            'price': travel_price,
            'amount': travel_price
        })
    
    # 後製相關加購項目
    st.subheader("後製相關加購項目")
    
    # 後製相關加購項目
    st.subheader("後製相關加購項目")
    
    # 網路用精修選項
    if is_photography_project:
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = "網路用精修"
            item_config = photography_add_ons["後製相關"][item_name]
            include_web_retouch = st.checkbox(f"加購{item_config['description']}", key="addon_web_retouch")
            
            if include_web_retouch:
                quantity = st.number_input(
                    "張數",
                    min_value=1,
                    value=1,
                    key=f"addon_{item_name}_quantity"
                )
                
                add_on_items.append({
                    'name': item_name,
                    'spec': item_config["spec"],
                    'quantity': quantity,
                    'price': item_config["price"],
                    'amount': item_config["price"] * quantity
                })
        
        # 大圖精修選項
        with col2:
            item_name = "大圖精修"
            item_config = photography_add_ons["後製相關"][item_name]
            include_large_retouch = st.checkbox(f"加購{item_config['description']}", key="addon_large_retouch")
            
            if include_large_retouch:
                quantity = st.number_input(
                    "張數",
                    min_value=1,
                    value=1,
                    key=f"addon_{item_name}_quantity"
                )
                
                add_on_items.append({
                    'name': item_name,
                    'spec': item_config["spec"],
                    'quantity': quantity,
                    'price': item_config["price"],
                    'amount': item_config["price"] * quantity
                })
    
    # 調光調色選項
    item_name = "調光調色"
    item_config = photography_add_ons["後製相關"][item_name]
    include_color_adjustment = st.checkbox(f"加購{item_config['description']} ${item_config['price']}", key="addon_color_adjustment")
    
    if include_color_adjustment:
        add_on_items.append({
            'name': item_name,
            'spec': item_config["spec"],
            'quantity': 1,
            'price': item_config["price"],
            'amount': item_config["price"]
        })
    
    # 場地相關項目
    st.subheader("場地相關項目")
    
    # 攝影棚選項
    item_name = "攝影棚"
    item_config = photography_add_ons["場地相關"][item_name]
    include_studio = st.checkbox(f"加購{item_config['description']}", key="addon_studio")
    
    if include_studio:
        studio_hours = st.number_input(
            "時數",
            min_value=1,
            value=2,
            key=f"addon_{item_name}_hours"
        )
        
        add_on_items.append({
            'name': item_name,
            'spec': item_config["spec"],
            'quantity': studio_hours,
            'price': item_config["price"],
            'amount': item_config["price"] * studio_hours
        })
    
    # 交通相關選項 - 更小且放在攝影棚之後
    st.markdown("##### 交通相關")
    
    # 車馬費選項
    item_name = "車馬費"
    item_config = photography_add_ons["交通相關"][item_name]
    options = item_config["options"]
    option_labels = [option["label"] for option in options]
    
    selected_index = st.selectbox(
        f"{item_name}",
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
            'price': selected_value,
            'amount': selected_value
        })
    
    # 自訂項目
    st.subheader("其他自訂項目")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        custom_name = st.text_input("項目名稱", key="custom_name")
    with col2:
        custom_spec = st.text_input("規格描述", key="custom_spec")
    with col3:
        custom_price = st.number_input("單價", min_value=0, step=100, key="custom_price")
    with col4:
        custom_quantity = st.number_input("數量", min_value=0, value=1, key="custom_quantity")
    
    if custom_name and custom_price > 0 and custom_quantity > 0:
        custom_amount = custom_price * custom_quantity
        add_on_items.append({
            'name': custom_name,
            'spec': custom_spec,
            'quantity': custom_quantity,
            'price': custom_price,
            'amount': custom_amount
        })
    
    # 報價單預覽和生成區塊
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 生成報價單按鈕
        st.subheader("產生報價單")
        st.info("報價單將以HTML格式生成，可直接列印為PDF")
        generate_button = st.button("產生報價單", use_container_width=True)
        
        if generate_button:
            if not client_name:
                st.error("請輸入客戶名稱")
            elif shoot_hours <= 0:
                st.error("拍攝時數必須大於0")
            else:
                with st.spinner("正在生成報價單..."):
                    # 生成HTML報價單
                    html_content = generate_html_quote(
                        client_name, 
                        project_type, 
                        shoot_hours, 
                        add_on_items,
                        video_options
                    )
                    
                    # 生成成功
                    st.success('報價單已生成！')
                    
                    # 提供HTML下載連結
                    st.markdown(
                        get_html_download_link(
                            html_content, 
                            f"報價單_{client_name}_{datetime.datetime.now().strftime('%Y%m%d')}.html"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    # 顯示HTML使用說明
                    st.info("""
                    **如何使用HTML報價單：**
                    1. 點擊上方連結下載HTML檔案
                    2. 用瀏覽器打開該檔案
                    3. 點擊頁面底部的「列印報價單」按鈕，或使用瀏覽器的列印功能（Ctrl+P或⌘+P）
                    4. 選擇「另存為PDF」將其儲存為PDF檔案
                    """)
                    
                    # 顯示預覽（可選）
                    with st.expander("點此預覽報價單"):
                        st.components.v1.html(html_content, height=500)
    
    with col2:
        # 顯示即時預覽
        if client_name and project_type:
            st.subheader("報價單預覽")
            
            # 客戶信息預覽
            preview_cols = st.columns(3)
            with preview_cols[0]:
                st.write(f"**客戶名稱**：{client_name}")
            with preview_cols[1]:
                st.write(f"**專案類型**：{project_type}")
            with preview_cols[2]:
                st.write(f"**拍攝時數**：{shoot_hours} 小時")
            
            # 影片規格顯示
            if video_options:
                video_cols = st.columns(2)
                with video_cols[0]:
                    if video_options.get("video_length"):
                        st.write(f"**影片長度**：{video_options['video_length']}")
                with video_cols[1]:
                    if video_options.get("orientation"):
                        st.write(f"**影片方向**：{video_options['orientation']}")
            
            # 計算基本費用
            hourly_rate = current_project.get("hourly_rate", 0)
            base_amount = hourly_rate * shoot_hours
            
            # 顯示費用預覽
            st.markdown("---")
            
            # 分類顯示項目明細
            st.write("### 項目明細")
            
            # 攝影基本費用
            st.write(f"**攝影費用**：{shoot_hours}小時 x ${hourly_rate:,}/小時 = **${base_amount:,}**")
            
            # 分類顯示加購項目
            if add_on_items:
                # 拍攝相關項目
                shoot_related = [item for item in add_on_items if item['name'] in ['平面攝助', '燈光設備', '美術費', '道具費', '車馬費']]
                if shoot_related:
                    st.write("**拍攝相關項目**：")
                    for item in shoot_related:
                        st.write(f"- {item['name']} ({item['spec']}) = **${item['amount']:,}**")
                
                # 後製相關項目
                post_related = [item for item in add_on_items if item['name'] in ['照片精修']]
                if post_related:
                    st.write("**後製相關項目**：")
                    for item in post_related:
                        st.write(f"- {item['name']} ({item['spec']}) = **${item['amount']:,}**")
                
                # 其他項目
                other_items = [item for item in add_on_items if item not in shoot_related and item not in post_related]
                if other_items:
                    st.write("**其他項目**：")
                    for item in other_items:
                        st.write(f"- {item['name']} ({item['spec']}) x {item['quantity']} = **${item['amount']:,}**")
            
            # 計算總費用
            additional_amount = sum(item['amount'] for item in add_on_items)
            subtotal = base_amount + additional_amount
            tax = subtotal * TAX_RATE
            total = subtotal + tax
            
            # 總計
            st.markdown("---")
            st.write(f"**基本攝影費**：${base_amount:,}")
            if additional_amount > 0:
                st.write(f"**額外項目**：${additional_amount:,}")
            st.write(f"**小計**：${subtotal:,}")
            st.write(f"**稅金（{int(TAX_RATE*100)}%）**：${tax:,}")
            st.markdown(f"### **總計（含稅）：${total:,}**")

# 運行應用
if __name__ == "__main__":
    main()

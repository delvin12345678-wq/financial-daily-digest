// 股票代號 / 公司名對照 —— 由 stock_names.py 移植,供新聞 ticker 比對用。

export const US_NAMES = {
  AAPL: ["蘋果", "Apple"], MSFT: ["微軟", "Microsoft"], GOOGL: ["谷歌", "Alphabet"],
  GOOG: ["谷歌", "Alphabet"], AMZN: ["亞馬遜", "Amazon"], META: ["Meta", "Meta"],
  NVDA: ["輝達", "Nvidia"], TSLA: ["特斯拉", "Tesla"], AMD: ["超微", "AMD"],
  TSM: ["台積電 ADR", "TSMC"], ARM: ["安謀", "Arm"], JPM: ["摩根大通", "JPMorgan"],
  GS: ["高盛", "Goldman Sachs"], "BRK-B": ["波克夏", "Berkshire"], AVGO: ["博通", "Broadcom"],
  NFLX: ["網飛", "Netflix"], INTC: ["英特爾", "Intel"], MU: ["美光", "Micron"],
  QCOM: ["高通", "Qualcomm"], PLTR: ["Palantir", "Palantir"], COST: ["好市多", "Costco"],
  DIS: ["迪士尼", "Disney"], BABA: ["阿里巴巴", "Alibaba"], SMCI: ["美超微", "Supermicro"],
  MSTR: ["微策略", "MicroStrategy"], COIN: ["Coinbase", "Coinbase"], UBER: ["優步", "Uber"],
  CRM: ["賽富時", "Salesforce"], ORCL: ["甲骨文", "Oracle"], ADBE: ["奧多比", "Adobe"],
  PYPL: ["PayPal", "PayPal"], BA: ["波音", "Boeing"], WMT: ["沃爾瑪", "Walmart"],
  KO: ["可口可樂", "Coca-Cola"], MCD: ["麥當勞", "McDonald's"], NKE: ["耐吉", "Nike"],
  V: ["Visa", "Visa"], MA: ["萬事達卡", "Mastercard"], XOM: ["艾克森美孚", "ExxonMobil"],
  LLY: ["禮來", "Eli Lilly"], JNJ: ["嬌生", "Johnson & Johnson"], UNH: ["聯合健康", "UnitedHealth"],
  IONQ: ["IonQ", "IonQ"], QBTS: ["D-Wave", "D-Wave"], QUBT: ["Quantum Computing", "Quantum Computing"],
  RGTI: ["Rigetti", "Rigetti"], VZ: ["威訊", "Verizon"], PFE: ["輝瑞", "Pfizer"],
  SFTBY: ["軟銀", "SoftBank"], T: ["AT&T", "AT&T"], CSCO: ["思科", "Cisco"],
  IBM: ["IBM", "IBM"], GE: ["奇異", "GE"], MRK: ["默克", "Merck"],
  ABBV: ["艾伯維", "AbbVie"], HD: ["家得寶", "Home Depot"], C: ["花旗", "Citigroup"],
  BAC: ["美國銀行", "Bank of America"], WFC: ["富國銀行", "Wells Fargo"], MS: ["摩根士丹利", "Morgan Stanley"],
  SBUX: ["星巴克", "Starbucks"], GME: ["遊戲驛站", "GameStop"], DELL: ["戴爾", "Dell"],
  HPQ: ["惠普", "HP"], MRVL: ["邁威爾", "Marvell"], ASML: ["艾司摩爾", "ASML"],
  MARA: ["Marathon", "Marathon Digital"], RIOT: ["Riot", "Riot Platforms"],
};

export const TW_NAMES = {
  "2330": ["台積電", "TSMC"], "2454": ["聯發科", "MediaTek"], "2317": ["鴻海", "Hon Hai"],
  "2308": ["台達電", "Delta"], "2382": ["廣達", "Quanta"], "2379": ["瑞昱", "Realtek"],
  "2303": ["聯電", "UMC"], "3008": ["大立光", "Largan"], "2412": ["中華電", "Chunghwa Telecom"],
  "2881": ["富邦金", "Fubon"], "2882": ["國泰金", "Cathay"], "6531": ["精測", "CHPT"],
  "3711": ["日月光投控", "ASE"], "2891": ["中信金", "CTBC"], "2603": ["長榮", "Evergreen"],
  "2002": ["中鋼", "China Steel"], "1301": ["台塑", "Formosa Plastics"], "3034": ["聯詠", "Novatek"],
  "3037": ["欣興", "Unimicron"], "2357": ["華碩", "ASUS"], "3231": ["緯創", "Wistron"],
  "2376": ["技嘉", "Gigabyte"], "2615": ["萬海", "Wan Hai"], "2609": ["陽明", "Yang Ming"],
};

export function displayName(code) {
  const c = String(code || "").trim().toUpperCase();
  const e = US_NAMES[c] || TW_NAMES[c];
  if (!e) return c;
  const [cn, en] = e;
  return cn && en && cn !== en ? `${cn} ${en}` : cn || c;
}

// 從一段文字抓出提及的股票代號:比對 ticker 符號(≥3 字才用詞界比對,避免 C/V/T 誤命中)
// 與公司中英文名。
export function extractTickers(text) {
  const raw = text || "";
  const upper = raw.toUpperCase();
  const hits = new Set();
  const scan = (names) => {
    for (const [code, [cn, en]] of Object.entries(names)) {
      if (code.length >= 3) {
        const re = new RegExp(`(^|[^A-Z0-9])${code.replace("-", "\\-")}([^A-Z0-9]|$)`);
        if (re.test(upper)) hits.add(code);
      } else if (/^\d+$/.test(code) && raw.includes(code)) {
        hits.add(code);
      }
      if (en && en.length > 3 && upper.includes(en.toUpperCase())) hits.add(code);
      if (cn && cn.length > 1 && raw.includes(cn)) hits.add(code);
    }
  };
  scan(US_NAMES);
  scan(TW_NAMES);
  return [...hits];
}

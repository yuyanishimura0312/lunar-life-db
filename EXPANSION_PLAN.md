# 月面生活リサーチDB 拡充計画

## 現状分析

| 指標 | 現状 | 目標 |
|------|------|------|
| エントリ数 | 100件 | 500件 |
| ソース数 | 49件 | 200件 |
| 課題数 | 10件 | 30件 |
| カテゴリ数 | 10 | 10（変更なし） |
| 国・地域 | 7カ国（重複あり） | 15カ国以上 |

## Phase 1: データ品質改善（既存100件の整備）

### 1-1. 国コード正規化
現在、同一国に複数コードが混在している（US/USA, JP/JPN, DE/DEU, NL/NLD）。
ISO 3166-1 alpha-2に統一する。

### 1-2. エントリ内容の充実
- description が空のエントリに詳細説明を追加
- source_url の欠損補完
- TRL評価の精緻化（根拠付き）

### 1-3. relations テーブルの構築
現在0件。エントリ間の関連（complements, extends, depends_on, competes_with）を定義する。

## Phase 2: 量的拡充（100件→300件）

### 2-1. JAXAブックレット深掘り（+50件）
「Space Life on the Moon」内で言及される具体的プロジェクト・技術を個別エントリ化。
- 月面基地モジュール設計（居住棟、温室、医療施設）
- JAXA月面農業実験
- ISS実験からの月面応用事例

### 2-2. 主要宇宙機関の公開研究（+80件）
| ソース | 対象 | 想定件数 |
|--------|------|----------|
| NASA HRP (Human Research Program) | 有人宇宙医学・心理学 | 20件 |
| ESA MELiSSA | 閉鎖生態系・水再生 | 15件 |
| CNSA 月面基地計画 | 中国の月面居住構想 | 10件 |
| ISRO Chandrayaan関連 | インドの月面資源利用 | 10件 |
| Roscosmos | ロシアの月面基地構想 | 5件 |
| 大学・研究機関 | MIT, 東大, ETH等の個別研究 | 20件 |

### 2-3. 民間企業の月面生活技術（+70件）
| 分野 | 企業例 | 想定件数 |
|------|--------|----------|
| 建設・3Dプリント | ICON, AI SpaceFactory, Lunar Resources | 15件 |
| 食料生産 | Interstellar Lab, Nanoracks | 10件 |
| 医療・遠隔手術 | Proximie, Virtual Incision | 10件 |
| 通信 | Nokia Bell Labs (4G/5G on Moon) | 5件 |
| エネルギー | Astrobotic, Lunar Outpost | 10件 |
| テキスタイル | ILC Dover, Collins Aerospace | 5件 |
| 生命維持 | Paragon Space Development | 5件 |
| 娯楽・メンタルヘルス | VR/AR各社の宇宙応用研究 | 10件 |

## Phase 3: 深層拡充（300件→500件）

### 3-1. 学術論文ベース（+100件）
Semantic Scholar / arXiv / PubMed から以下の検索クエリで収集:
- "lunar habitat" / "moon base life support"
- "space agriculture closed loop"
- "microgravity health countermeasures"
- "ISRU water extraction"
- "space radiation shielding habitat"
- "isolation confinement psychology space"
- "3D printing lunar regolith"
- "telemedicine space exploration"

### 3-2. 極地・海底アナログ環境（+50件）
月面生活の地上シミュレーション環境からの知見:
| アナログ | 内容 | 想定件数 |
|----------|------|----------|
| HI-SEAS (Hawaii) | 長期隔離居住実験 | 10件 |
| Mars Desert Research Station | 火星/月面模擬生活 | 8件 |
| Concordia Station (南極) | 極限環境の居住 | 8件 |
| NEEMO (海底) | 水中居住・EVA訓練 | 8件 |
| Biosphere 2 | 閉鎖生態系の教訓 | 8件 |
| 中国月宮一号 | 閉鎖生態系実験 | 8件 |

### 3-3. 課題テーブル拡充（10件→30件）
各カテゴリの課題を3件に増やし、以下を追加:
- 放射線防護（医療）
- 月面レゴリスの人体影響（衛生）
- 低重力下の骨密度低下（運動）
- 通信遅延によるメンタルヘルス影響（通信）
- 水のリサイクル効率（水）
- 長期食料保存（食）
- 閉鎖空間のストレス（娯楽/睡眠）
- 月面ダスト対策（衣服/作業環境）

## Phase 4: 構造拡張

### 4-1. 新テーブル: modules（月面基地モジュール）
JAXAブックレットの月面基地設計図をベースに、各モジュールの情報をDB化。
```
modules: id, name_ja, name_en, module_type, description, area_m2, 
         capacity, life_support_systems, image_url
```

### 4-2. 新テーブル: roadmap（開発ロードマップ）
Artemis計画等の公式タイムラインと各技術の実用化見通しを紐付け。
```
roadmap: id, milestone, organization, target_year, status, 
         description, related_entries
```

### 4-3. 新テーブル: experts（専門家・研究者）
各分野の主要研究者を記録し、エントリとリンク。
```
experts: id, name, affiliation, country, field, publications_count,
         h_index, profile_url
```

## 収集方法

### 自動収集（collect_web.py拡張）
1. NASA Technical Reports Server API
2. ESA公開データベース
3. arXiv API (astro-ph, physics.space-ph)
4. Semantic Scholar API
5. Google Scholar（Playwrightスクレイピング）

### 手動キュレーション
- JAXAブックレット内の具体的プロジェクト抽出
- 月面基地コンペ（3D Printed Habitat Challenge等）の応募作品
- 宇宙建築学会・IAF（国際宇宙連盟）の発表資料

## 実行スケジュール

| Phase | 内容 | 想定エントリ数 |
|-------|------|---------------|
| Phase 1 | データ品質改善 | 100件（既存整備） |
| Phase 2 | 量的拡充 | +200件 = 300件 |
| Phase 3 | 深層拡充 | +200件 = 500件 |
| Phase 4 | 構造拡張 | テーブル追加 |

## 優先度

1. **最優先**: Phase 1（品質改善）— 既存データの信頼性確保
2. **高**: Phase 2-1, 2-2（JAXAブックレット深掘り+宇宙機関）— コアコンテンツ
3. **中**: Phase 2-3, 3-1（民間企業+論文）— 幅の拡大
4. **後回し可**: Phase 3-2, 4（アナログ環境+構造拡張）— 深さの追加

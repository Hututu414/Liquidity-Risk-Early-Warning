# Literature Integration Audit

## Source Files Read

- `01_materials/literature/文献综述_编号引用_中文术语版.md`
- `08_report/latex_project/sections/02_literature.tex`
- `08_report/latex_project/refs.bib`
- `08_report/latex_project/main.tex`

## Section Replacement

- The original literature-review section was replaced and restructured.
- The new section keeps a compact three-subsection structure:
  1. 高频市场状态、流动性压力与已实现测度
  2. 动态风险度量、RGARCH-CARR-SK 与 QVAR 尾部传导
  3. 机器学习金融预警、SMARTBoost 与本文边际贡献
- The text was converted from the markdown literature review into LaTeX prose and aligned with this paper's empirical chain: minute-level OHLCV and turnover information, LSI as a short-horizon liquidity-pressure proxy, RGARCH-CARR-SK as dynamic risk measurement, QVAR as tail-quantile transmission and stress testing, and SMARTBoost as out-of-sample event warning.

## Citation Handling

- Markdown-style numbered citations were converted to BibTeX citations in the LaTeX section.
- The final compile log reports:
  - undefined references: 0
  - missing files: 0
  - citation warnings: 0
- No mixed raw numbered citation format remains in `sections/02_literature.tex`.

## BibTeX Entries Added

The following entries from the markdown BibTeX draft were merged into `08_report/latex_project/refs.bib` while preserving existing project entries:

- `madhavan2000survey`
- `andersen2003realized`
- `chordia2001liquidity`
- `aitsahalia2009noise`
- `peng2024chinamicrostructure`
- `cobandag2022liquidityreview`
- `gu2007bidaskchina`
- `goyenko2009liquidity`
- `corwin2012spread`
- `barndorff2004bipower`
- `martens2007range`
- `chou2005carr`
- `amihud2002illiquidity`
- `engle1982arch`
- `bollerslev1986garch`
- `hansen2012realizedgarch`
- `liu2025rgarchcarrsk`
- `koenker1978rq`
- `white2015varforvar`
- `holopainen2016earlywarning`
- `suss2019bankdistress`
- `friedman2001gbm`

## Duplicate or Related Entries Identified

- `andersen2003modeling` already existed and is related to, but not the same key as, the added `andersen2003realized`.
- `barndorff2004power` already existed and is related to, but not the same key as, the added `barndorff2004bipower`.
- `liu2025rgarch` already existed but was incomplete for the paper's RGARCH-CARR-SK citation. The literature review and RGARCH section now cite `liu2025rgarchcarrsk`.
- `koenker2005quantile` already existed as a monograph entry and was preserved alongside the foundational `koenker1978rq`.

## SMARTBoost Reference Status

- Existing project entry `giordani2025smartboost` was retained and cited for SMARTBoost.
- No DOI, page range, or extra bibliographic metadata was fabricated.
- The SMARTBoost title and venue metadata should still be treated as needing final bibliographic verification before formal submission.

## Literature-to-Use Table

- The 23-row markdown table was not inserted verbatim into the paper.
- A compressed three-column table was added to the literature review:
  - 文献脉络
  - 代表文献
  - 本文用途
- This keeps the literature map useful for readers without creating a long, fragile table in the main text.

## Risk Notes

- No suspected fabricated citation was introduced by this integration step.
- The only remaining bibliographic risk is the SMARTBoost entry's final metadata verification.
- The final PDF has no undefined citation or missing bibliography warnings.

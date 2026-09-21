# 官方依据与刷新规则

原表核验日期：2026-09-13；2026-09-21补核下表Google AI optimization、FAQ变更、生成式AI报告及资格设置，其余来源本轮未重新核验。链接用于支持对应条目，不代表网站研究已经获得任何客户结果。执行时涉及当前规格/规则再查官方原文；地域、平台、账户能力分别验证。其余页面设计与工作流为本方法的设计建议，不冒充官方强制规范。

| 官方来源 | 支持的规则 | 不可推断 |
|---|---|---|
| [Google AI features](https://developers.google.com/search/docs/appearance/ai-features) | AI搜索沿用SEO基础资格，Search Console Web类型包含相应流量 | 满足资格不保证抓取/索引/引用；不能从总Web流量精确分离所有AI曝光 |
| [Google AI optimization](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)（2026-09-21） | 原创有用内容；Google忽略llms.txt，不要求专用GEO文件或特殊schema | 不能推导其他平台相同行为，也不能承诺文件、文章数或schema换来排名/引用 |
| [生成式AI表现报告](https://support.google.com/webmasters/answer/16984139) / [资格设置](https://support.google.com/webmasters/answer/16908024)（2026-09-21） | 核获授权属性报表可用性；展示量与采样/引荐分列；设置及继承只读核查 | 不能推断跨平台曝光、训练许可或业务结果；不可自动修改属性设置 |
| [Google搜索文档变更：2026年5月](https://developers.google.com/search/updates#may-2026)（2026-09-21） | Google自2026-05-07起不再展示FAQ富结果 | 不代表有用的可见问答应删除，也不代表其他搜索平台采用相同策略 |
| [web.dev Web Vitals](https://web.dev/articles/vitals) | LCP≤2.5s、INP≤200ms、CLS≤0.1；现场第75百分位分设备评估 | 单次Lighthouse不能证明现场CWV，TBT不是实测INP |
| [Lab and field](https://web.dev/articles/lab-and-field-data-differences) | 受控测试用于复现，真实用户数据用于现场判断 | 实验室结果不是所有用户的体验 |
| [Shopify theme performance](https://shopify.dev/docs/storefronts/themes/best-practices/performance/index) | 首屏图优先、非首屏懒加载、响应式CDN与固有尺寸 | 不能将Shopify专用语法强制用于其他平台 |
| [Shopify responsive design](https://shopify.dev/docs/storefronts/themes/best-practices/performance/implement-responsive-design) | 按显示尺寸选择资源与移动裁切 | 两套CSS隐藏大图不等于只下载一套 |
| [W3C tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) | tab/tablist/tabpanel、键盘、焦点及激活模型 | 鼠标可点不代表无障碍完成 |
| [W3C animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | 非必要交互运动可禁用，尊重减少动态偏好 | 此AAA条目不能冒称全部网站已满足WCAG；合规需完整范围检查 |
| [OpenAI model catalog](https://developers.openai.com/api/docs/models) / [Codex model guidance](https://learn.chatgpt.com/docs/models) | 用当前官方模型定位与宿主选项区分能力、模型和推理设置 | 文档中的模型不保证当前账户可选；提示词角色不证明实际路由 |

更新时保存新核验日期、变化条目和受影响验收，不因某篇营销文章更换整套方法。模型选择参考页不作为冻结模型ID；实际选择留在项目工作单。

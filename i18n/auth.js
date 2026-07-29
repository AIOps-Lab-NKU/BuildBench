window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };

const buildBenchAuthTranslations = Object.freeze({
  "Team Registration | Build-Bench Challenge": "团队注册 | Build-Bench Challenge",
  "Sign In | Build-Bench Challenge": "登录 | Build-Bench Challenge",
  "My Team | Build-Bench Challenge": "我的团队 | Build-Bench Challenge",
  "Already registered? Sign in": "已经注册？前往登录",
  "Competition registration": "竞赛注册",
  "Register your team": "注册参赛团队",
  "The team captain creates one account and records the complete team roster. Other members do not need separate accounts.":
    "由队长创建一个账号并录入完整团队名单，其他组员无需单独注册账号。",
  "Captain account": "队长账号",
  "This person manages submissions and the team roster.": "队长负责管理 Agent 提交和团队名单。",
  "Full name": "姓名",
  "Email": "邮箱",
  "Institution": "学校或机构",
  "Password": "密码",
  "At least 12 characters.": "至少 12 个字符。",
  "Confirm password": "确认密码",
  "Team details": "团队信息",
  "Team names and member emails must be unique within this competition.":
    "本次竞赛中的团队名和组员邮箱均不可重复。",
  "Team name": "团队名称",
  "Team roster": "团队名单",
  "The captain is member 1. Add up to four additional members.":
    "队长为第 1 位成员，最多可再添加 4 位组员。",
  "Add team member": "添加组员",
  "Confirm registration": "确认注册",
  "Check the roster carefully before creating the team.": "创建团队前请仔细核对名单。",
  "I confirm that the information is accurate and accept the competition rules.":
    "我确认以上信息准确，并接受竞赛规则。",
  "competition rules": "竞赛规则",
  "Create team account": "创建团队账号",
  "Email verification is not required in the current registration phase.":
    "当前注册阶段暂不要求邮箱验证。",
  "Registration rules": "注册规则",
  "One captain, one team": "一名队长，一个团队",
  "One captain account manages the team.": "仅队长账号负责管理团队。",
  "Teams may contain 1–5 people, including the captain.":
    "每队包含 1–5 人，队长计入人数。",
  "Every member email is required.": "所有组员邮箱均为必填项。",
  "An email cannot appear in another team.": "同一邮箱不能出现在其他团队。",
  "The leaderboard displays the team name only.": "排行榜仅展示团队名称。",
  "Roster lock": "名单锁定",
  "The organizer will announce when rosters become immutable. Until then, the captain may update non-captain members.":
    "组委会将另行公布名单锁定时间；锁定前，队长可以修改非队长成员。",
  "Remove member": "移除组员",
  "Build-Bench competition team and captain account.": "Build-Bench 竞赛团队与队长账号注册。",
  "Continue your Build-Bench submission": "继续管理 Build-Bench 参赛提交",
  "Sign in as the team captain to manage the roster, upload Agent versions, and follow official evaluations.":
    "队长登录后可管理团队名单、上传 Agent 版本并查看正式评测。",
  "Manage one immutable Agent version at a time.": "管理不可变的 Agent 提交版本。",
  "Run Hosted Smoke Tests before formal evaluation.": "正式评测前运行 Hosted Smoke Test。",
  "Track Full Evaluation results for your team.": "查看团队的完整评测结果。",
  "Captain access": "队长入口",
  "Sign in": "登录",
  "Use the captain email registered for your team.": "请使用团队注册时填写的队长邮箱。",
  "Not registered yet?": "尚未注册？",
  "Register a team": "注册团队",
  "Team registration": "团队注册",
  "My Team": "我的团队",
  "Manage the public team name and member roster used for this competition.":
    "管理本次竞赛使用的公开团队名称和成员名单。",
  "Loading team details…": "正在加载团队信息……",
  "Competition": "竞赛",
  "Registration status": "注册状态",
  "Registration active": "可编辑名单",
  "Team ID": "团队 ID",
  "Public identity": "公开身份",
  "This is the only team identity shown on the public leaderboard.":
    "这是排行榜上唯一公开展示的团队身份。",
  "Save team name": "保存团队名称",
  "Registration roster": "参赛名单",
  "Team members": "团队成员",
  "Every email is required and may appear in only one team.":
    "所有邮箱均为必填项，且只能出现在一个团队中。",
  "Name": "姓名",
  "Actions": "操作",
  "Account owner": "账号负责人",
  "Captain": "队长",
  "Edit": "编辑",
  "Remove": "移除",
  "Edit team member": "编辑组员",
  "Close": "关闭",
  "Cancel": "取消",
  "Save member": "保存组员",
  "My Submissions": "我的提交",
  "Sign out": "退出登录",
  "Register team": "注册团队",
});

["register", "login", "team"].forEach((page) => {
  window.BuildBenchI18nData.pages[page] = buildBenchAuthTranslations;
});

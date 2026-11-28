using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Text.Json;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Antiforgery;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddAntiforgery(options => options.FormFieldName = "__RequestVerificationToken");
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.Cookie.Name = "AgriVision.Admin";
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Strict;
        options.ExpireTimeSpan = TimeSpan.FromMinutes(25);
        options.SlidingExpiration = false;
        options.LoginPath = "/login";
    });
builder.Services.AddAuthorization();
builder.Services.AddHttpClient("AgriVisionApi", client =>
{
    var baseUrl = builder.Configuration["AgriVisionApi:BaseUrl"] ?? "http://localhost:8000";
    client.BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/");
    client.Timeout = TimeSpan.FromSeconds(10);
});

var app = builder.Build();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.UseAntiforgery();

app.MapGet("/", () => Results.Redirect("/dashboard"));

app.MapGet("/login", (HttpContext context, IAntiforgery antiforgery) =>
{
    var token = antiforgery.GetAndStoreTokens(context).RequestToken;
    return Results.Content($"""
        <!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
        <title>دخول الإدارة | AgriVision</title><style>{Ui.Css}</style><main class="login"><h1>AgriVision</h1><p>لوحة الإدارة الزراعية</p>
        <form method="post" action="/login"><input type="hidden" name="__RequestVerificationToken" value="{E(token)}">
        <label>اسم المستخدم أو البريد<input name="username" required autocomplete="username"></label>
        <label>كلمة المرور<input type="password" name="password" required autocomplete="current-password"></label>
        <button>تسجيل الدخول</button></form></main></html>
        """, "text/html; charset=utf-8");
}).AllowAnonymous();

app.MapPost("/login", async (HttpContext context, IHttpClientFactory clients, IAntiforgery antiforgery) =>
{
    await antiforgery.ValidateRequestAsync(context);
    var form = await context.Request.ReadFormAsync();
    using var client = clients.CreateClient("AgriVisionApi");
    using var response = await client.PostAsync("api/v1/auth/login",
        new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["username"] = form["username"].ToString(), ["password"] = form["password"].ToString()
        }));
    if (!response.IsSuccessStatusCode)
        return Results.Content(LoginError("تعذر تسجيل الدخول. تحقق من البيانات أو تواصل مع مسؤول النظام."), "text/html; charset=utf-8", statusCode: 401);
    using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
    var accessToken = json.RootElement.GetProperty("access_token").GetString();
    if (string.IsNullOrWhiteSpace(accessToken)) return Results.Problem("لم يرجع الخادم رمز دخول.", statusCode: 502);
    var identity = new ClaimsIdentity(new[] { new Claim("api_token", accessToken) }, CookieAuthenticationDefaults.AuthenticationScheme);
    await context.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(identity));
    return Results.Redirect("/dashboard");
}).AllowAnonymous();

app.MapPost("/logout", async (HttpContext context, IAntiforgery antiforgery) =>
{
    await antiforgery.ValidateRequestAsync(context);
    await context.SignOutAsync();
    return Results.Redirect("/login");
}).RequireAuthorization();

app.MapGet("/dashboard", async (HttpContext context, IHttpClientFactory clients, IAntiforgery antiforgery) =>
{
    var token = context.User.FindFirstValue("api_token");
    if (token is null) return Results.Redirect("/login");
    using var client = clients.CreateClient("AgriVisionApi");
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
    var summary = await GetJson(client, "api/v1/admin/dashboard");
    if (summary is null) return Results.Content(Page("تعذر تحميل لوحة الإدارة", "تأكد من اتصال FastAPI ومن أن حسابك يحمل دور admin.", context, antiforgery), "text/html; charset=utf-8", statusCode: 503);
    var analytics = await GetJson(client, "api/v1/admin/analytics?days=14");
    var diagnostics = await GetJson(client, "api/v1/admin/diagnostics");
    var users = await GetJson(client, "api/v1/admin/users?limit=20");
    var crops = await GetJson(client, "api/v1/admin/crops?limit=100");
    var models = await GetJson(client, "api/v1/admin/models?limit=100");
    var cards = string.Join("", summary.RootElement.EnumerateObject().Select(p => $"<article class='card'><span>{E(Label(p.Name))}</span><strong>{E(p.Value.ToString())}</strong></article>"));
    var body = $"<section class='health'>{Diagnostics(diagnostics)}</section><section class='cards'>{cards}</section>" +
        Analytics(analytics) + "<section class='grid'>" +
        Table("المستخدمون (آخر 20)", users, new[] { "username", "email", "role", "is_active" }) +
        Table("المحاصيل", crops, new[] { "name_ar", "name", "scientific_name", "is_supported" }) +
        Table("إصدارات النماذج", models, new[] { "name", "version", "status" }) + "</section>" +
        "<a class='button' href='/reports/summary.csv'>تنزيل تقرير CSV</a><p class='footnote'>المؤشرات من قاعدة بيانات الخدمة المتصلة، وقد تكون فارغة في بيئة جديدة.</p>";
    return Results.Content(Page("نظرة عامة", body, context, antiforgery, true), "text/html; charset=utf-8");
}).RequireAuthorization();

app.MapGet("/reports/summary.csv", async (HttpContext context, IHttpClientFactory clients) =>
{
    using var client = clients.CreateClient("AgriVisionApi");
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", context.User.FindFirstValue("api_token"));
    using var response = await client.GetAsync("api/v1/admin/reports/summary.csv");
    if (!response.IsSuccessStatusCode) return Results.StatusCode((int)response.StatusCode);
    return Results.File(await response.Content.ReadAsByteArrayAsync(), "text/csv; charset=utf-8", "agrivision-summary.csv");
}).RequireAuthorization();

app.MapPost("/users/{id:guid}/active", async (Guid id, HttpContext context, IHttpClientFactory clients, IAntiforgery antiforgery) =>
{
    await antiforgery.ValidateRequestAsync(context);
    var form = await context.Request.ReadFormAsync();
    var active = string.Equals(form["is_active"], "true", StringComparison.OrdinalIgnoreCase);
    using var client = clients.CreateClient("AgriVisionApi");
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", context.User.FindFirstValue("api_token"));
    using var response = await client.PatchAsync($"api/v1/admin/users/{id}/active", JsonContent.Create(new { is_active = active }));
    return response.IsSuccessStatusCode ? Results.Redirect("/dashboard") : Results.StatusCode((int)response.StatusCode);
}).RequireAuthorization();

app.MapPost("/crops/{id:guid}/support", async (Guid id, HttpContext context, IHttpClientFactory clients, IAntiforgery antiforgery) =>
{
    await antiforgery.ValidateRequestAsync(context);
    var form = await context.Request.ReadFormAsync();
    var supported = string.Equals(form["is_supported"], "true", StringComparison.OrdinalIgnoreCase);
    using var client = clients.CreateClient("AgriVisionApi");
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", context.User.FindFirstValue("api_token"));
    using var response = await client.PatchAsync($"api/v1/admin/crops/{id}/support", JsonContent.Create(new { is_supported = supported }));
    return response.IsSuccessStatusCode ? Results.Redirect("/dashboard") : Results.StatusCode((int)response.StatusCode);
}).RequireAuthorization();

app.MapPost("/models/{id:guid}/{operation}", async (Guid id, string operation, HttpContext context, IHttpClientFactory clients, IAntiforgery antiforgery) =>
{
    await antiforgery.ValidateRequestAsync(context);
    if (operation is not ("deploy" or "rollback")) return Results.BadRequest();
    using var client = clients.CreateClient("AgriVisionApi");
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", context.User.FindFirstValue("api_token"));
    using var response = await client.PostAsync($"api/v1/studio/models/{id}/{operation}",
        operation == "deploy" ? JsonContent.Create(new { target = "server", config = new { } }) : null);
    return response.IsSuccessStatusCode ? Results.Redirect("/dashboard") : Results.StatusCode((int)response.StatusCode);
}).RequireAuthorization();

app.Run();

static async Task<JsonDocument?> GetJson(HttpClient client, string path)
{
    try
    {
        using var response = await client.GetAsync(path);
        if (!response.IsSuccessStatusCode) return null;
        return JsonDocument.Parse(await response.Content.ReadAsStringAsync());
    }
    catch (HttpRequestException) { return null; }
    catch (TaskCanceledException) { return null; }
}

static string Table(string title, JsonDocument? data, string[] fields)
{
    if (data is null) return $"<article class='panel'><h2>{E(title)}</h2><p class='muted'>تعذر جلب البيانات من الخدمة.</p></article>";
    var rows = new List<string>();
    foreach (var item in data.RootElement.EnumerateArray())
    {
        var cells = string.Join("", fields.Select(field => $"<td>{E(item.TryGetProperty(field, out var v) ? v.ToString() : "—")}</td>"));
        var action = "";
        if (item.TryGetProperty("id", out var id) && item.TryGetProperty("is_active", out var isActive))
            action = $"<td><form method='post' action='/users/{E(id.ToString())}/active'><input type='hidden' name='__RequestVerificationToken' value='{{TOKEN}}'><input type='hidden' name='is_active' value='{(!isActive.GetBoolean()).ToString().ToLowerInvariant()}'><button class='small'>{(isActive.GetBoolean() ? "إيقاف" : "تفعيل")}</button></form></td>";
        else if (item.TryGetProperty("id", out id) && item.TryGetProperty("is_supported", out var isSupported))
            action = $"<td><form method='post' action='/crops/{E(id.ToString())}/support'><input type='hidden' name='__RequestVerificationToken' value='{{TOKEN}}'><input type='hidden' name='is_supported' value='{(!isSupported.GetBoolean()).ToString().ToLowerInvariant()}'><button class='small'>{(isSupported.GetBoolean() ? "إلغاء الدعم" : "تفعيل الدعم")}</button></form></td>";
        else if (item.TryGetProperty("id", out id) && item.TryGetProperty("status", out var modelStatus))
        {
            var status = modelStatus.ToString();
            var operation = status.Equals("ready", StringComparison.OrdinalIgnoreCase) ? "deploy" :
                status.Equals("deployed", StringComparison.OrdinalIgnoreCase) ? "rollback" : "";
            if (operation.Length > 0)
                action = $"<td><form method='post' action='/models/{E(id.ToString())}/{operation}' onsubmit=\"return confirm('تأكيد { (operation == "deploy" ? "نشر" : "التراجع عن نشر") } النموذج؟')\"><input type='hidden' name='__RequestVerificationToken' value='{{TOKEN}}'><button class='small'>{(operation == "deploy" ? "نشر" : "تراجع")}</button></form></td>";
            else action = "<td>غير جاهز للنشر</td>";
        }
        rows.Add($"<tr>{cells}{action}</tr>");
    }
    var hasAction = fields.Contains("is_active") || fields.Contains("is_supported") || fields.Contains("status");
    var headings = string.Join("", fields.Select(field => $"<th>{E(Label(field))}</th>")) + (hasAction ? "<th>إجراء</th>" : "");
    var content = rows.Count == 0 ? "<p class='empty'>لا توجد سجلات لعرضها حالياً.</p>" : $"<div class='scroll'><table><thead><tr>{headings}</tr></thead><tbody>{string.Join("", rows)}</tbody></table></div>";
    return $"<article class='panel'><h2>{E(title)}</h2>{content}</article>";
}

static string Analytics(JsonDocument? data)
{
    if (data is null)
        return "<article class='panel analytics'><h2>نشاط التحليل</h2><p class='muted'>تعذر تحميل بيانات التحليل.</p></article>";

    var root = data.RootElement;
    var daily = root.GetProperty("daily_analyses").EnumerateArray().ToArray();
    var max = Math.Max(1, daily.Select(x => x.GetProperty("count").GetInt32()).DefaultIfEmpty(0).Max());
    const double chartWidth = 900;
    const double chartHeight = 190;
    const double top = 22;
    const double plotHeight = 125;
    var slot = chartWidth / Math.Max(1, daily.Length);
    var barWidth = Math.Min(34, slot * .56);
    var bars = new List<string>();
    for (var i = 0; i < daily.Length; i++)
    {
        var item = daily[i];
        var count = item.GetProperty("count").GetInt32();
        var date = item.GetProperty("date").GetString() ?? "";
        var height = count == 0 ? 2 : Math.Max(4, plotHeight * count / max);
        var x = i * slot + (slot - barWidth) / 2;
        var y = top + plotHeight - height;
        var label = date.Length >= 10 ? date[5..10] : date;
        bars.Add($"<g><title>{E(date)}: {count}</title><rect x='{x:F1}' y='{y:F1}' width='{barWidth:F1}' height='{height:F1}' rx='5' class='bar'/><text x='{x + barWidth / 2:F1}' y='{top + plotHeight + 23:F1}' text-anchor='middle'>{E(label)}</text></g>");
    }

    var statusRows = root.GetProperty("statuses").EnumerateArray().Select(item =>
    {
        var key = item.GetProperty("status").GetString() ?? "unknown";
        var count = item.GetProperty("count").GetInt32();
        return $"<div class='stat-row'><span>{E(StatusLabel(key))}</span><strong>{count}</strong></div>";
    }).ToArray();
    var labels = root.GetProperty("top_result_labels").EnumerateArray().Select(item =>
    {
        var name = item.GetProperty("label").GetString() ?? "—";
        var count = item.GetProperty("count").GetInt32();
        return $"<div class='stat-row'><span>{E(name)}</span><strong>{count}</strong></div>";
    }).ToArray();
    var statusContent = statusRows.Length == 0 ? "<p class='empty'>لا توجد عمليات في الفترة.</p>" : string.Join("", statusRows);
    var labelContent = labels.Length == 0 ? "<p class='empty'>لا توجد نتائج مسجلة في الفترة.</p>" : string.Join("", labels);
    return $"<section class='analytics-grid'><article class='panel analytics'><div class='panel-heading'><div><h2>نشاط التحليل</h2><p class='muted'>آخر {root.GetProperty("window_days").GetInt32()} يوماً · UTC</p></div></div><svg class='chart' viewBox='0 0 {chartWidth} {chartHeight}' role='img' aria-label='عدد عمليات التحليل اليومية'>{string.Join("", bars)}</svg></article>" +
        $"<article class='panel'><h2>حالات العمليات</h2>{statusContent}</article><article class='panel'><h2>أكثر النتائج تسجيلاً</h2>{labelContent}</article></section>";
}

static string Diagnostics(JsonDocument? data)
{
    if (data is null) return "<span class='health-bad'><i></i> تعذر قراءة صحة الخدمة أو قاعدة البيانات</span>";
    var root = data.RootElement;
    var api = root.TryGetProperty("api", out var apiValue) ? apiValue.GetString() : null;
    var database = root.TryGetProperty("database", out var dbValue) ? dbValue.GetString() : null;
    var apiOk = string.Equals(api, "healthy", StringComparison.OrdinalIgnoreCase);
    var dbOk = string.Equals(database, "healthy", StringComparison.OrdinalIgnoreCase);
    return $"<span class='{(apiOk ? "health-ok" : "health-bad")}'><i></i> API: {(apiOk ? "متصل" : "غير متاح")}</span><span class='{(dbOk ? "health-ok" : "health-bad")}'><i></i> قاعدة البيانات: {(dbOk ? "متصلة" : "غير متاحة")}</span>";
}

static string Page(string title, string body, HttpContext context, IAntiforgery antiforgery, bool authenticated = false)
{
    var token = antiforgery.GetAndStoreTokens(context).RequestToken;
    body = body.Replace("{TOKEN}", E(token));
    var logout = authenticated ? $"<form method='post' action='/logout'><input type='hidden' name='__RequestVerificationToken' value='{E(token)}'><button class='small'>خروج</button></form>" : "";
    return $"<!doctype html><html lang='ar' dir='rtl'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{E(title)} | AgriVision</title><style>{Ui.Css}</style><header><b>AgriVision</b><span>لوحة الإدارة الزراعية</span>{logout}</header><main><h1>{E(title)}</h1>{body}</main></html>";
}

static string LoginError(string message) => $"<!doctype html><html lang='ar' dir='rtl'><meta charset='utf-8'><style>{Ui.Css}</style><main class='login'><h1>تعذر الدخول</h1><p>{E(message)}</p><a class='button' href='/login'>العودة</a></main></html>";
static string E(string? value) => HtmlEncoder.Default.Encode(value ?? "—");
static string StatusLabel(string key) => key.ToLowerInvariant() switch { "completed" => "مكتملة", "success" => "ناجحة", "failed" => "فاشلة", "processing" => "قيد المعالجة", "pending" => "بانتظار المعالجة", "cancelled" or "canceled" => "ملغاة", _ => key };
static string Label(string key) => key switch { "users" => "المستخدمون", "farms" => "المزارع", "crops" => "المحاصيل", "analyses" => "التحليلات", "datasets" => "مجموعات البيانات", "models" => "النماذج", "training_runs" => "تشغيلات التدريب", "username" => "المستخدم", "email" => "البريد", "role" => "الدور", "is_active" => "نشط", "name_ar" => "الاسم العربي", "name" => "الاسم", "scientific_name" => "الاسم العلمي", "is_supported" => "مدعوم", "version" => "الإصدار", "status" => "الحالة", _ => key };
static class Ui
{
    public const string Css = "*{box-sizing:border-box}body{margin:0;background:#f4f7f2;color:#17352d;font:16px system-ui}header{display:flex;gap:20px;align-items:center;padding:18px 5%;background:#123c32;color:white}header form{margin-right:auto}main{max-width:1320px;margin:32px auto;padding:0 22px}h1{font-size:30px;margin:0 0 22px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:14px}.card,.panel,.login{background:#fff;border:1px solid #dce7df;border-radius:16px;padding:20px;box-shadow:0 8px 25px #102b2010}.card span,.card strong{display:block}.card span,.muted,.footnote{color:#6d8176}.card strong{font-size:30px;margin-top:8px}.grid,.analytics-grid{display:grid;gap:18px;margin:22px 0}.panel h2{font-size:19px;margin:0 0 14px}.analytics{min-width:0}.chart{width:100%;height:auto;overflow:visible}.chart text{fill:#6d8176;font-size:12px}.bar{fill:#36896a}.analytics-grid{grid-template-columns:minmax(0,2fr) minmax(210px,1fr)}.analytics-grid .panel:last-child{grid-column:2}.health{display:flex;gap:22px;flex-wrap:wrap;margin-bottom:16px;padding:12px 16px;background:#fff;border-radius:12px;border:1px solid #dce7df}.health-ok,.health-bad{display:inline-flex;gap:8px;align-items:center;font-size:14px}.health-ok i,.health-bad i{width:8px;height:8px;border-radius:50%;background:#228455}.health-bad i{background:#c44c42}.stat-row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #edf1ed}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:right;padding:10px;border-bottom:1px solid #edf1ed}.button,button{border:0;border-radius:9px;background:#197653;color:#fff;padding:10px 16px;text-decoration:none;cursor:pointer}.small{padding:7px 11px}.empty{padding:14px;color:#6d8176;background:#f7f9f7;border-radius:10px}.footnote{font-size:13px;margin-top:14px}.login{max-width:430px;margin:10vh auto}.login label{display:block;margin:16px 0}.login input:not([type=hidden]){display:block;width:100%;padding:12px;margin-top:6px;border:1px solid #ccd9d0;border-radius:8px}.login button{width:100%}@media(max-width:850px){.analytics-grid{grid-template-columns:1fr}.analytics-grid .panel:last-child{grid-column:auto}.grid{grid-template-columns:1fr}}";
}

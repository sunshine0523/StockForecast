using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using SemanticKernelService.Config;
using SemanticKernelService.Database;
using SemanticKernelService.Filter;
using SemanticKernelService.Utils;

var builder = WebApplication.CreateBuilder(args);

//数据库
builder.Services.AddDbContext<MySqlDatabaseContext>(option =>
{
    string connectionString = builder.Configuration.GetConnectionString("MySQLStockConnection")!;
    var serverVersion = ServerVersion.AutoDetect(connectionString);
    option.UseMySql(connectionString, serverVersion);
});

//跨域
builder.Services.AddCors(options =>
{
    options.AddPolicy(
        name: "MyPolicy",
        policyBuilder =>
        {
            policyBuilder.WithOrigins("http://localhost:8080");
            policyBuilder.AllowAnyMethod();
            policyBuilder.AllowAnyHeader();
        }
    );
});

// 身份验证
JWTTokenOptions tokenOptions = new JWTTokenOptions();
builder.Configuration.Bind("JWTTokenOptions", tokenOptions);
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        //JWT默认属性  
        //是否验证Issuer
        ValidateIssuer = true,
        //是否验证Audience
        ValidateAudience = true,
        //似乎否验证失效时间  
        ValidateLifetime = true,  
        //是否验证SecurityKey
        ValidateIssuerSigningKey = true,  
        //与签发JWT设置一致
        ValidAudience = tokenOptions.Audience,  
        //与签发JWT设置一致
        ValidIssuer = tokenOptions.Issuer,  
        //获取SecurityKey
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(tokenOptions.SecurityKey))
    };
});
builder.Services.AddSingleton(new JwtHelper(tokenOptions));

builder.Services.AddControllers(configure =>
{
    configure.Filters.Add<ActionFilter>();
});

builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "WebApplication", Version = "v1" });

    c.AddSecurityDefinition("bearerAuth", new OpenApiSecurityScheme
    {
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
    });
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "bearerAuth"
                }
            },
            new string[] { }
        }
    });
});

builder.Services.AddHttpClient();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseCors("MyPolicy");

app.UseAuthorization();
app.UseAuthentication();

app.MapControllers();

app.Run();
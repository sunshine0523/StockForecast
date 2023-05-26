using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Graph.ExternalConnectors;
using SemanticKernelService.Model;
using SemanticKernelService.Services;
using SemanticKernelService.Services.impl;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Controllers;

[ApiController]
[EnableCors("MyPolicy")]
[Route("[controller]")]
public class AuthenticationController : ControllerBase
{
    private readonly ILogger<AuthenticationController> _logger;
    private readonly IAuthenticationService _authenticationService;
    private readonly JwtHelper _jwtHelper;
    private readonly IConfigurationRoot _configuration;

    public AuthenticationController(ILogger<AuthenticationController> logger, JwtHelper jwtHelper)
    {
        _logger = logger;
        _jwtHelper = jwtHelper;
        _authenticationService = new AuthenticationService();
        var configurationBuilder = new ConfigurationBuilder();
        configurationBuilder.SetBasePath(Directory.GetCurrentDirectory()).AddJsonFile("appsettings.json");
        _configuration = configurationBuilder.Build();
    }
    
    [HttpPost("authentication")]
    public async Task<ActionResult<UserTokenInfo>> AuthenticationAsync([FromBody] OpenAiConfig? openAiConfig)
    {
        if (null == openAiConfig)
        {
            _logger.LogError("UserParam is null");
            return Unauthorized();
        }
        var openAiValidResult = await _authenticationService.ToValidOpenAiAsync(openAiConfig);
        if (openAiValidResult == ValidResult.SUCCESS)
        {
            var token = _jwtHelper.CreateToken(openAiConfig);
            _authenticationService.AddLoginUser(token, openAiConfig, _configuration["ConnectionStrings:MySQLStockConnection"], _logger);
            return new UserTokenInfo(token);
        }

        return Unauthorized();
    }

    /// <summary>
    /// 验证token是否有效
    /// </summary>
    /// <returns></returns>
    [HttpGet("valid")]
    [Authorize(AuthenticationSchemes = JwtBearerDefaults.AuthenticationScheme)]
    public ActionResult<string> Valid()
    {
        
        try
        {
            var token = HttpContext.Request.Headers["Authorization"].ToString().Split(" ")[1];
            var validResult = _authenticationService.ToValidToken(token);
            return validResult;
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            return Unauthorized();
        }
    }
}
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using SemanticKernelService.Model;
using SemanticKernelService.Services;
using SemanticKernelService.Services.impl;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Controllers;

[ApiController]
[Route("[controller]")]
public class AuthenticationController : ControllerBase
{
    private readonly ILogger<AuthenticationController> _logger;
    private readonly IOpenAiAuthenticationService _openAiAuthenticationService;
    private readonly JwtHelper _jwtHelper;

    public AuthenticationController(ILogger<AuthenticationController> logger, JwtHelper jwtHelper)
    {
        _logger = logger;
        _jwtHelper = jwtHelper;
        _openAiAuthenticationService = new OpenAiAuthenticationService();
    }

    [HttpPost(Name = "login")]
    public async Task<ActionResult<UserTokenInfo>> LoginAsync([FromBody] OpenAiConfig? openAiConfig)
    {
        if (null == openAiConfig || 
            null == openAiConfig.DeploymentOrModel ||
            null == openAiConfig.Endpoint ||
            null == openAiConfig.Key)
        {
            _logger.LogError("UserParam is null");
            return Unauthorized();
        }
        var openAiValidResult = await _openAiAuthenticationService.ToValidOpenAiAsync(openAiConfig);
        if (openAiValidResult == OpenAiValidResult.SUCCESS)
        {
            var token = _jwtHelper.CreateToken();
            _openAiAuthenticationService.AddLoginUser(token, openAiConfig, _logger);
            return new UserTokenInfo(token);
        }

        return Unauthorized();
    }
}
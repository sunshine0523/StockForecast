using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using SemanticKernelService.Model;
using SemanticKernelService.Services;
using SemanticKernelService.Services.impl;

namespace SemanticKernelService.Controllers;

[ApiController]
[Route("[controller]")]
[EnableCors("MyPolicy")]
[Authorize(AuthenticationSchemes = JwtBearerDefaults.AuthenticationScheme)]
public class SemanticKernelController : ControllerBase
{
    private readonly ILogger<SemanticKernelController> _logger;
    private readonly ISkService _skService;

    public SemanticKernelController(ILogger<SemanticKernelController> logger)
    {
        _logger = logger;
        _skService = new SkService();
    }

    [HttpPost("skills/{skillName}/invoke/{functionName}")]
    public async Task<ActionResult<AskResult>> InvokeFunctionAsync(string skillName, string functionName, Ask? ask)
    {
        try
        {
            var token = HttpContext.Request.Headers["Authorization"].ToString().Split(" ")[1];
            var askResult = await _skService.InvokeFunction(token, skillName, functionName, ask);
            return new ActionResult<AskResult>(askResult);
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            return BadRequest(e.Message);
        }
    }
}
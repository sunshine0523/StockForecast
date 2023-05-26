using System.IdentityModel.Tokens.Jwt;
using Microsoft.AspNetCore.Mvc.Filters;
using SemanticKernelService.Model;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Filter;

/// <summary>
/// 拦截器判断token是否过期
/// </summary>
public class ActionFilter : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext context)
    {
        base.OnActionExecuting(context);
        try
        {
            var token = context.HttpContext.Request.Headers["Authorization"].ToString().Split(" ")[1];
            ValidToken(token);
        }
        catch (Exception)
        {
            // ignored
        }
    }

    private void ValidToken(string token)
    {
        var jsonToken = new JwtSecurityTokenHandler().ReadToken(token);
        // token已经过期
        if (jsonToken.ValidTo.GetTimeStamp() <= DateTime.Now.GetTimeStamp())
        {
            Console.WriteLine("Token已经过期，移除登录用户");
            LoginUser.LoginUserList.Remove(token);
        }
    }
}
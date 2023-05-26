using System.Collections;
using System.IdentityModel.Tokens.Jwt;
using SemanticKernelService.Database;
using SemanticKernelService.Model;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Services.impl;

public class AuthenticationService : IAuthenticationService
{
    public async Task<ValidResult> ToValidOpenAiAsync(OpenAiConfig param)
    {
        ValidResult result;
        try
        {
            result = await OpenAiUtils.ToValidOpenAiAsync(param);
        }
        catch (Exception)
        {
            result = ValidResult.FAIL;
        }

        return result;
    }

    public void AddLoginUser(string token, OpenAiConfig openAiConfig, string mysqlConnectionString, ILogger logger)
    {
        var kernel = SemanticKernelFactory.CreateKernel(openAiConfig, mysqlConnectionString, logger);
        LoginUser.LoginUserList.Add(token, kernel);
    }

    public string ToValidToken(string token)
    {
        JwtSecurityToken? jsonToken = new JwtSecurityTokenHandler().ReadToken(token) as JwtSecurityToken;
        // token已经过期
        if (null == jsonToken || !LoginUser.LoginUserList.ContainsKey(token) || jsonToken.ValidTo.GetTimeStamp() <= DateTime.Now.GetTimeStamp())
        {
            throw new Exception("Token expire");
        }

        return jsonToken.Payload["Deployment"].ToString()!;
    }
}
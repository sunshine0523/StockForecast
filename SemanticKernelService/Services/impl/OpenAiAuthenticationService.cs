using SemanticKernelService.Model;
using SemanticKernelService.Utils;

namespace SemanticKernelService.Services.impl;

public class OpenAiAuthenticationService : IOpenAiAuthenticationService
{
    public async Task<OpenAiValidResult> ToValidOpenAiAsync(OpenAiConfig param)
    {
        return await OpenAiUtils.ToValidOpenAiAsync(param);
    }

    public void AddLoginUser(string token, OpenAiConfig openAiConfig, ILogger logger)
    {
        var kernel = SemanticKernelFactory.CreateKernel(openAiConfig, logger);
        LoginUser.LoginUserList.Add(token, kernel);
    }
}
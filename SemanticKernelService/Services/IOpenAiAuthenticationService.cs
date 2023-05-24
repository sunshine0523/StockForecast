using Microsoft.SemanticKernel;
using SemanticKernelService.Model;

namespace SemanticKernelService.Services;

public interface IOpenAiAuthenticationService
{
    public Task<OpenAiValidResult> ToValidOpenAiAsync(OpenAiConfig param);
    public void AddLoginUser(string token, OpenAiConfig openAiConfig, ILogger logger);
}

public enum OpenAiValidResult
{
    SUCCESS,
    FAIL
}
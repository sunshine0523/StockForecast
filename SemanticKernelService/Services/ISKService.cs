using SemanticKernelService.Model;

namespace SemanticKernelService.Services;

public interface ISkService
{
    public Task<AskResult> InvokeFunction(string token, string skillName, string functionName, Ask? ask);
}
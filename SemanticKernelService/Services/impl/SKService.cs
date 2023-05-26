using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Orchestration;
using SemanticKernelService.Model;

namespace SemanticKernelService.Services.impl;

public class SkService : ISkService
{
    public async Task<AskResult> InvokeFunction(string token, string skillName, string functionName, Ask? ask)
    {
        var kernel = LoginUser.LoginUserList[token] as IKernel;
        if (null == kernel) throw new NullReferenceException("Kernel is null");

        var skFunction = kernel.Skills.GetFunction(skillName, functionName);

        ContextVariables contextVariables;
        if (null != ask)
        {
            contextVariables = new ContextVariables(ask.Value);
            foreach (var input in ask.Inputs)
            {
                contextVariables.Set(input.Key, input.Value);
            }
        }
        else
        {
            contextVariables = new ContextVariables();
        }
        
        var result = await kernel.RunAsync(contextVariables, skFunction);
        if (result.ErrorOccurred)
        {
            throw new Exception("SK ErrorOccurred");
        }

        return new AskResult
        {
            Value = result.Result, 
            State = result.Variables.Select(v => 
                new AskInput { Key = v.Key, Value = v.Value }
            )
        };
    }
}
using System.Collections;
using Microsoft.SemanticKernel;

namespace SemanticKernelService.Model;

internal static class LoginUser
{
    internal static Dictionary<string, IKernel> LoginUserList { get; } = new();
}
using System.Text.RegularExpressions;

namespace SemanticKernelService.Utils;

public static class TextUtils
{
    /// <summary>
    /// 只保留汉字、字母和数字
    /// </summary>
    /// <param name="source"></param>
    /// <returns></returns>
    public static string ReplaceSpecialSymbol(this string source)
    {
        string pattern = "[A-Za-z0-9\u4e00-\u9fa5-]+";
        string matchStr = "";
        MatchCollection results = Regex.Matches(source, pattern);
        foreach (var s in results)
        {
            matchStr += s.ToString();
        }
        return matchStr;
    }
}
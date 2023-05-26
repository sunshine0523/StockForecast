namespace SemanticKernelService.Utils;

public static class DateTimeUtils
{
    public static long GetTimeStamp(this DateTime dateTime)
    {
        DateTime dateTime1970 = new DateTime(1970, 1, 1).ToLocalTime();
        return (long) (dateTime.ToLocalTime() - dateTime1970).TotalSeconds;
    }
    
    /// <summary>
    /// 根据时间戳返回交易日日期
    /// 规则：如果新闻发生在9-15点，那么算作当天交易日
    /// 如果新闻发生在15点到次日9点，那么算作次日交易日
    /// </summary>
    /// <param name="timeScamp">时间戳</param>
    /// <returns>所属交易日期：2022-5-23</returns>
    public static string GetTransactionDate(this int timeScamp)
    {
        var time = new DateTime(1970, 1, 1, 8, 0, 0).AddSeconds(timeScamp);
        if (time.Hour >= 15)
        {
            time = time.AddDays(1);
        }

        return time.Year + "-" + time.Month + "-" + time.Day;
    }
}
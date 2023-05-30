using Microsoft.EntityFrameworkCore;

namespace SemanticKernelService.Database;

public class MySqlDatabaseContext : DbContext
{
    public MySqlDatabaseContext(){}
    public MySqlDatabaseContext(DbContextOptions<MySqlDatabaseContext> options) : base(options) { }
    public DbSet<StockNews> StockNews { get; set; }
    public DbSet<NewsEmotion> NewsEmotion { get; set; }
}
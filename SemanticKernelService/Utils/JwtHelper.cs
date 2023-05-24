using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using SemanticKernelService.Config;
using SemanticKernelService.Model;
using JwtRegisteredClaimNames = Microsoft.IdentityModel.JsonWebTokens.JwtRegisteredClaimNames;

namespace SemanticKernelService.Utils;

public class JwtHelper
{
    private readonly JWTTokenOptions _jwtTokenOptions;

    public JwtHelper(JWTTokenOptions jwtTokenOptions)
    {
        _jwtTokenOptions = jwtTokenOptions;
    }

    public string CreateToken()
    {
        var claims = new[]
        {
            new Claim(ClaimTypes.Name, "u_admin"),
            new Claim(ClaimTypes.Role, "r_admin"),
            new Claim(JwtRegisteredClaimNames.Jti, "admin")
        };
        var secretKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtTokenOptions.SecurityKey));
        var algorithm = SecurityAlgorithms.HmacSha256;
        var signingCredentials = new SigningCredentials(secretKey, algorithm);
        var jwtSecurityToken = new JwtSecurityToken(
            _jwtTokenOptions.Issuer,
            _jwtTokenOptions.Audience,
            claims,
            DateTime.Now,
            DateTime.Now.AddSeconds(30),
            signingCredentials);
        return new JwtSecurityTokenHandler().WriteToken(jwtSecurityToken);
    }
}
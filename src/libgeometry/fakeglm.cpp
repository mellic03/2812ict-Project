#include "fakeglm.hpp"
#include <cmath>


float
glm::dot(const glm::vec3 &u, const glm::vec3 &v)
{
    return u.x*v.x + u.y*v.y + u.z*v.z;
}


glm::vec3
glm::cross(const glm::vec3 &u, const glm::vec3 &v)
{
    return {
         u.y*v.z - u.z*v.y,
       -(u.x*v.z - u.z*v.x),
         u.x*v.y - u.y*v.x
    };
}


float
glm::mag( const glm::vec3 &v )
{
    return sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
}


glm::vec3
glm::normalize(glm::vec3 v)
{
    v /= glm::mag(v);
    return v;
}


float 
glm::angle(const glm::vec3 &u, const glm::vec3 &v)
{
    float theta = acos( glm::dot(u, v) / (glm::mag(u) * glm::mag(v)) );
    return theta;
}


glm::vec3
operator + (const glm::vec3 &u, const glm::vec3 &v)
{
    return {u.x+v.x, u.y+v.y, u.z+v.z};
}


glm::vec3 &
operator += (glm::vec3 &u, const glm::vec3 &v)
{
    u.x += v.x;  u.y += v.y;  u.z += v.z;
    return u;
}


glm::vec3
operator * ( const float &f, const glm::vec3 &v )
{
    return { f*v.x, f*v.y, f*v.z };
}


glm::vec3
operator - (const glm::vec3 &u, const glm::vec3 &v)
{
    return { u.x-v.x, u.y-v.y, u.z-v.z };
}


glm::vec3 &
operator /= (glm::vec3 &v, float f)
{
    v.x /= f;  v.y /= f;  v.z /= f;
    return v;
}

// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:srv/GetMove.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__SRV__DETAIL__GET_MOVE__TRAITS_HPP_
#define INTERFACES__SRV__DETAIL__GET_MOVE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interfaces/srv/detail/get_move__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetMove_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: fen
  {
    out << "fen: ";
    rosidl_generator_traits::value_to_yaml(msg.fen, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetMove_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: fen
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fen: ";
    rosidl_generator_traits::value_to_yaml(msg.fen, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetMove_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace interfaces

namespace rosidl_generator_traits
{

[[deprecated("use interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const interfaces::srv::GetMove_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::srv::GetMove_Request & msg)
{
  return interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::srv::GetMove_Request>()
{
  return "interfaces::srv::GetMove_Request";
}

template<>
inline const char * name<interfaces::srv::GetMove_Request>()
{
  return "interfaces/srv/GetMove_Request";
}

template<>
struct has_fixed_size<interfaces::srv::GetMove_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interfaces::srv::GetMove_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interfaces::srv::GetMove_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetMove_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: move
  {
    out << "move: ";
    rosidl_generator_traits::value_to_yaml(msg.move, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetMove_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: move
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "move: ";
    rosidl_generator_traits::value_to_yaml(msg.move, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetMove_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace interfaces

namespace rosidl_generator_traits
{

[[deprecated("use interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const interfaces::srv::GetMove_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::srv::GetMove_Response & msg)
{
  return interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::srv::GetMove_Response>()
{
  return "interfaces::srv::GetMove_Response";
}

template<>
inline const char * name<interfaces::srv::GetMove_Response>()
{
  return "interfaces/srv/GetMove_Response";
}

template<>
struct has_fixed_size<interfaces::srv::GetMove_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interfaces::srv::GetMove_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interfaces::srv::GetMove_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::srv::GetMove>()
{
  return "interfaces::srv::GetMove";
}

template<>
inline const char * name<interfaces::srv::GetMove>()
{
  return "interfaces/srv/GetMove";
}

template<>
struct has_fixed_size<interfaces::srv::GetMove>
  : std::integral_constant<
    bool,
    has_fixed_size<interfaces::srv::GetMove_Request>::value &&
    has_fixed_size<interfaces::srv::GetMove_Response>::value
  >
{
};

template<>
struct has_bounded_size<interfaces::srv::GetMove>
  : std::integral_constant<
    bool,
    has_bounded_size<interfaces::srv::GetMove_Request>::value &&
    has_bounded_size<interfaces::srv::GetMove_Response>::value
  >
{
};

template<>
struct is_service<interfaces::srv::GetMove>
  : std::true_type
{
};

template<>
struct is_service_request<interfaces::srv::GetMove_Request>
  : std::true_type
{
};

template<>
struct is_service_response<interfaces::srv::GetMove_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__SRV__DETAIL__GET_MOVE__TRAITS_HPP_

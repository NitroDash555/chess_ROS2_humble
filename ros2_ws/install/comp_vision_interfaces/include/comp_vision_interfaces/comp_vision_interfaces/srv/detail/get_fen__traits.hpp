// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from comp_vision_interfaces:srv/GetFEN.idl
// generated code does not contain a copyright notice

#ifndef COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__TRAITS_HPP_
#define COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "comp_vision_interfaces/srv/detail/get_fen__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace comp_vision_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetFEN_Request & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetFEN_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetFEN_Request & msg, bool use_flow_style = false)
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

}  // namespace comp_vision_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use comp_vision_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const comp_vision_interfaces::srv::GetFEN_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  comp_vision_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use comp_vision_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const comp_vision_interfaces::srv::GetFEN_Request & msg)
{
  return comp_vision_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<comp_vision_interfaces::srv::GetFEN_Request>()
{
  return "comp_vision_interfaces::srv::GetFEN_Request";
}

template<>
inline const char * name<comp_vision_interfaces::srv::GetFEN_Request>()
{
  return "comp_vision_interfaces/srv/GetFEN_Request";
}

template<>
struct has_fixed_size<comp_vision_interfaces::srv::GetFEN_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<comp_vision_interfaces::srv::GetFEN_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<comp_vision_interfaces::srv::GetFEN_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace comp_vision_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetFEN_Response & msg,
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
  const GetFEN_Response & msg,
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

inline std::string to_yaml(const GetFEN_Response & msg, bool use_flow_style = false)
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

}  // namespace comp_vision_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use comp_vision_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const comp_vision_interfaces::srv::GetFEN_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  comp_vision_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use comp_vision_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const comp_vision_interfaces::srv::GetFEN_Response & msg)
{
  return comp_vision_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<comp_vision_interfaces::srv::GetFEN_Response>()
{
  return "comp_vision_interfaces::srv::GetFEN_Response";
}

template<>
inline const char * name<comp_vision_interfaces::srv::GetFEN_Response>()
{
  return "comp_vision_interfaces/srv/GetFEN_Response";
}

template<>
struct has_fixed_size<comp_vision_interfaces::srv::GetFEN_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<comp_vision_interfaces::srv::GetFEN_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<comp_vision_interfaces::srv::GetFEN_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<comp_vision_interfaces::srv::GetFEN>()
{
  return "comp_vision_interfaces::srv::GetFEN";
}

template<>
inline const char * name<comp_vision_interfaces::srv::GetFEN>()
{
  return "comp_vision_interfaces/srv/GetFEN";
}

template<>
struct has_fixed_size<comp_vision_interfaces::srv::GetFEN>
  : std::integral_constant<
    bool,
    has_fixed_size<comp_vision_interfaces::srv::GetFEN_Request>::value &&
    has_fixed_size<comp_vision_interfaces::srv::GetFEN_Response>::value
  >
{
};

template<>
struct has_bounded_size<comp_vision_interfaces::srv::GetFEN>
  : std::integral_constant<
    bool,
    has_bounded_size<comp_vision_interfaces::srv::GetFEN_Request>::value &&
    has_bounded_size<comp_vision_interfaces::srv::GetFEN_Response>::value
  >
{
};

template<>
struct is_service<comp_vision_interfaces::srv::GetFEN>
  : std::true_type
{
};

template<>
struct is_service_request<comp_vision_interfaces::srv::GetFEN_Request>
  : std::true_type
{
};

template<>
struct is_service_response<comp_vision_interfaces::srv::GetFEN_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // COMP_VISION_INTERFACES__SRV__DETAIL__GET_FEN__TRAITS_HPP_

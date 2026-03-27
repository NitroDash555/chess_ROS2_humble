// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:srv/GetMove.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__SRV__DETAIL__GET_MOVE__BUILDER_HPP_
#define INTERFACES__SRV__DETAIL__GET_MOVE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/srv/detail/get_move__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace srv
{

namespace builder
{

class Init_GetMove_Request_fen
{
public:
  Init_GetMove_Request_fen()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::interfaces::srv::GetMove_Request fen(::interfaces::srv::GetMove_Request::_fen_type arg)
  {
    msg_.fen = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::srv::GetMove_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::srv::GetMove_Request>()
{
  return interfaces::srv::builder::Init_GetMove_Request_fen();
}

}  // namespace interfaces


namespace interfaces
{

namespace srv
{

namespace builder
{

class Init_GetMove_Response_move
{
public:
  Init_GetMove_Response_move()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::interfaces::srv::GetMove_Response move(::interfaces::srv::GetMove_Response::_move_type arg)
  {
    msg_.move = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::srv::GetMove_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::srv::GetMove_Response>()
{
  return interfaces::srv::builder::Init_GetMove_Response_move();
}

}  // namespace interfaces

#endif  // INTERFACES__SRV__DETAIL__GET_MOVE__BUILDER_HPP_

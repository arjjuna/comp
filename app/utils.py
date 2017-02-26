from models import User, Client, Prof, Message

from sqlalchemy import and_, or_

# These functions are not fully tested

def latest_message(message_list):
	""" Returns the latest message from a list """
	if len(message_list) == 0:
		return None
	message_list.sort(key=lambda x: x.timestamp)
	return message_list[-1]

def message_senders(message_list):
	""" Returns a list of senders from a message list """
	return list(set([m.sender for m in message_list]))





def latest_messages_by_sender(User, n=0):
	all_received = User.messages_received
	all_senders = message_senders(all_received.all())

	latest_by_sender = [
						(s,
						 latest_message(all_received.filter_by(sender=s).all())
						) for s in all_senders]
	if n and len(latest_by_sender) > n:
		return latest_by_sender[:n]
	else:
		return latest_by_sender


def conversation_query(user1, user2):
	conversation = Message.query.filter(or_(
								and_(Message.sender == user1, Message.receiver == user2),
								and_(Message.sender == user2, Message.receiver == user1)
										))

	return conversation.order_by(Message.timestamp.desc())

from app.chatbot import ConversationState, Step, next_messages


def test_happy_path_flow() -> None:
    state = ConversationState(user_id="54911223344")

    assert "asistente virtual" in next_messages(state, "hola")[0].lower()
    assert state.step == Step.ASK_FULL_NAME

    next_messages(state, "Juan Perez")
    assert state.step == Step.ASK_DNI

    next_messages(state, "30111222")
    assert state.step == Step.ASK_MEMBER_ID

    next_messages(state, "A-1234")
    assert state.step == Step.ASK_PROCEDURE

    next_messages(state, "2")
    assert state.step == Step.ASK_DETAILS

    replies = next_messages(state, "Necesito autorizar una resonancia.")
    assert state.step == Step.DONE
    assert state.ticket_id is not None
    assert any("número de gestión" in r.lower() for r in replies)


def test_invalid_dni() -> None:
    state = ConversationState(user_id="x")
    next_messages(state, "hola")
    next_messages(state, "Nombre Prueba")
    replies = next_messages(state, "12")
    assert "no parece válido" in replies[0].lower()

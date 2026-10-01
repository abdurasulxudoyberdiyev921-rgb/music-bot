import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from mido import Message, MidiFile, MidiTrack

# Sizing Telegram Bot Tokeningiz:
TOKEN = "8902470228:AAENHG5Irkwy12wfci2yw8rNd9-gLOQcT9E"

# Do-re-mi-fa-sol-lya-si-do gammasi
NOTES = [60, 62, 64, 65, 67, 69, 71, 72]

# Akkordlar ketma-ketligi
CHORDS = {
    "Pop": [[60, 64, 67], [67, 71, 74], [69, 72, 76], [65, 69, 72]], # C - G - Am - F
    "Lo-Fi": [[60, 63, 67, 70], [65, 68, 72, 75], [68, 72, 75, 78], [63, 67, 70, 74]], # Cmin7 - Fmin7 - G#maj7 - D#maj7
}

def generate_midi(style: str, filename: str = "music.mid"):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Pianino asbobini tanlash
    track.append(Message('program_change', program=0, time=0))
    selected_chords = CHORDS.get(style, CHORDS["Pop"])
    
    for chord in selected_chords:
        for note in chord:
            track.append(Message('note_on', note=note, velocity=80, time=0))
        for i, note in enumerate(chord):
            track.append(Message('note_off', note=note, velocity=80, time=480 if i == 0 else 0))
            
        extra_note = random.choice(NOTES)
        track.append(Message('note_on', note=extra_note, velocity=90, time=0))
        track.append(Message('note_off', note=extra_note, velocity=90, time=240))

    mid.save(filename)
    return filename

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎵 Pop Musiqa", callback_data="Pop"),
            InlineKeyboardButton("🎧 Lo-Fi Musiqa", callback_data="Lo-Fi"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Salom! Men musiqa (MIDI) yaratuvchi botman. Qaysi uslubda musiqa yaratamiz?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    style = query.data
    await query.edit_message_text(text=f"⏳ {style} uslubida musiqa yaratilmoqda...")
    
    file_path = f"{style}_music.mid"
    generate_midi(style, file_path)
    
    with open(file_path, 'rb') as audio_file:
        await query.message.reply_document(
            document=audio_file,
            filename=f"{style}_generated.mid",
            caption=f"✨ Siz uchun yaratilgan {style} uslubidagi MIDI fayl!"
        )
    
    if os.path.exists(file_path):
        os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
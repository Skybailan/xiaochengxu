import random
import re

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyWord, ProWord

COLUMN_SPLIT_PATTERN = re.compile(r'\t+|\s{2,}')
NULL_LITERALS = {'', 'null', 'none', 'nil', '-'}


class OpenIdRequiredMixin:
    def get_openid(self, request):
        openid = request.query_params.get('openid', '').strip()
        if not openid:
            raise ValueError('缺少 openid 参数')
        return openid


class ImportPayloadMixin:
    def get_import_payload(self, request):
        openid = str(request.data.get('openid', '')).strip()
        library_type = str(request.data.get('library_type', '')).strip().lower()
        raw_text = str(request.data.get('raw_text', '')).strip()

        if not openid:
            raise ValueError('缺少 openid 参数')
        if library_type not in {'daily', 'pro'}:
            raise ValueError('library_type 仅支持 daily 或 pro')
        if not raw_text:
            raise ValueError('请粘贴要导入的文本内容')

        return openid, library_type, raw_text


def shuffle_items(items):
    shuffled = list(items)
    random.shuffle(shuffled)
    return shuffled


def normalize_value(value):
    cleaned = value.strip()
    return '' if cleaned.lower() in NULL_LITERALS else cleaned


def split_columns(line):
    stripped = line.strip().strip('|')
    if not stripped:
        return []
    return [normalize_value(part) for part in COLUMN_SPLIT_PATTERN.split(stripped) if part.strip()]


def is_header_row(columns, library_type):
    joined = ' '.join(columns).lower()
    if library_type == 'daily':
        header_tokens = ['单词', '中文', '日常句']
    else:
        header_tokens = ['单词', '词性中文', '特殊记法', '日常句']
    return all(token in joined for token in header_tokens)


def pad_columns(columns, expected_count):
    padded = list(columns[:expected_count])
    while len(padded) < expected_count:
        padded.append('')
    return padded


def build_daily_defaults(translation, daily_sentence, daily_sentence_translation):
    return {
        'translation': translation or 'null',
        'daily_sentence': daily_sentence or 'null',
        'daily_sentence_translation': daily_sentence_translation or 'null',
    }


def build_pro_defaults(translation_with_pos, memory_method, daily_sentence, daily_sentence_translation):
    return {
        'translation_with_pos': translation_with_pos or 'null',
        'memory_method': memory_method or 'null',
        'daily_sentence': daily_sentence or 'null',
        'daily_sentence_translation': daily_sentence_translation or 'null',
    }


def build_daily_review_item(current_word, user_words):
    distractor_pool = [
        item for item in user_words if item.id != current_word.id and item.translation != current_word.translation
    ]
    distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))

    options = [
        {
            'word_id': current_word.id,
            'english_word': current_word.word,
            'label': current_word.translation,
            'is_correct': True,
        }
    ]
    options.extend(
        {
            'word_id': item.id,
            'english_word': item.word,
            'label': item.translation,
            'is_correct': False,
        }
        for item in distractors
    )

    return {
        'question_id': current_word.id,
        'word': current_word.word,
        'translation': current_word.translation,
        'hint': {
            'daily_sentence': current_word.daily_sentence,
            'daily_sentence_translation': current_word.daily_sentence_translation,
        },
        'options': shuffle_items(options),
    }


def extract_pos(translation_with_pos):
    match = re.match(r'\s*([a-zA-Z]+\.)', translation_with_pos)
    return match.group(1).lower() if match else ''


def pro_similarity_score(target, candidate):
    score = 0
    if target.word[:1].lower() == candidate.word[:1].lower():
        score += 4
    if abs(len(target.word) - len(candidate.word)) <= 1:
        score += 3
    elif abs(len(target.word) - len(candidate.word)) <= 2:
        score += 2

    target_pos = extract_pos(target.translation_with_pos)
    candidate_pos = extract_pos(candidate.translation_with_pos)
    if target_pos and target_pos == candidate_pos:
        score += 5

    shared_chars = set(target.word.lower()) & set(candidate.word.lower())
    score += min(len(shared_chars), 3)
    return score


def build_pro_review_item(current_word, user_words):
    candidate_pool = [
        item
        for item in user_words
        if item.id != current_word.id and item.translation_with_pos != current_word.translation_with_pos
    ]
    ranked_pool = sorted(
        candidate_pool,
        key=lambda item: (pro_similarity_score(current_word, item), random.random()),
        reverse=True,
    )

    distractors = ranked_pool[:3]
    if len(distractors) < 3:
        remaining = [item for item in candidate_pool if item not in distractors]
        random.shuffle(remaining)
        distractors.extend(remaining[: 3 - len(distractors)])

    options = [
        {
            'word_id': current_word.id,
            'english_word': current_word.word,
            'label': current_word.translation_with_pos,
            'is_correct': True,
        }
    ]
    options.extend(
        {
            'word_id': item.id,
            'english_word': item.word,
            'label': item.translation_with_pos,
            'is_correct': False,
        }
        for item in distractors
    )

    return {
        'question_id': current_word.id,
        'word': current_word.word,
        'translation': current_word.translation_with_pos,
        'hint': {
            'daily_sentence': current_word.daily_sentence,
            'daily_sentence_translation': current_word.daily_sentence_translation,
            'memory_method': current_word.memory_method,
        },
        'options': shuffle_items(options),
    }


class DailyReviewAPIView(OpenIdRequiredMixin, APIView):
    def get(self, request):
        try:
            openid = self.get_openid(request)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        words = list(DailyWord.objects.filter(user_openid=openid))
        random.shuffle(words)
        review_items = [build_daily_review_item(word, words) for word in words]

        return Response(
            {
                'mode': 'daily',
                'total': len(review_items),
                'items': review_items,
            }
        )


class ProReviewAPIView(OpenIdRequiredMixin, APIView):
    def get(self, request):
        try:
            openid = self.get_openid(request)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        words = list(ProWord.objects.filter(user_openid=openid))
        random.shuffle(words)
        review_items = [build_pro_review_item(word, words) for word in words]

        return Response(
            {
                'mode': 'pro',
                'total': len(review_items),
                'items': review_items,
            }
        )


class WordImportAPIView(ImportPayloadMixin, APIView):
    expected_column_map = {
        'daily': 4,
        'pro': 5,
    }

    @transaction.atomic
    def post(self, request):
        try:
            openid, library_type, raw_text = self.get_import_payload(request)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        lines = [line for line in raw_text.splitlines() if line.strip()]
        expected_columns = self.expected_column_map[library_type]
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_rows = []

        for index, line in enumerate(lines, start=1):
            columns = split_columns(line)
            if not columns:
                continue
            if index == 1 and is_header_row(columns, library_type):
                skipped_count += 1
                continue
            if len(columns) < 2:
                error_rows.append({'line': index, 'content': line, 'reason': '至少需要提供单词和释义'})
                continue

            padded_columns = pad_columns(columns, expected_columns)
            word = padded_columns[0]
            if not word:
                error_rows.append({'line': index, 'content': line, 'reason': '单词不能为空'})
                continue

            if library_type == 'daily':
                translation, daily_sentence, daily_sentence_translation = padded_columns[1], padded_columns[2], padded_columns[3]
                defaults = build_daily_defaults(translation, daily_sentence, daily_sentence_translation)
                _, created = DailyWord.objects.update_or_create(
                    user_openid=openid,
                    word=word,
                    defaults=defaults,
                )
            else:
                translation_with_pos = padded_columns[1]
                memory_method = padded_columns[2]
                daily_sentence = padded_columns[3]
                daily_sentence_translation = padded_columns[4]
                defaults = build_pro_defaults(
                    translation_with_pos,
                    memory_method,
                    daily_sentence,
                    daily_sentence_translation,
                )
                _, created = ProWord.objects.update_or_create(
                    user_openid=openid,
                    word=word,
                    defaults=defaults,
                )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response(
            {
                'message': '导入完成',
                'library_type': library_type,
                'openid': openid,
                'summary': {
                    'total_lines': len(lines),
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'skipped_count': skipped_count,
                    'error_count': len(error_rows),
                },
                'errors': error_rows[:20],
            }
        )

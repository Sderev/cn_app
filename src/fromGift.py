#!/usr/bin/python3
#-*- coding: utf-8 -*-

import yattag
import logging
import re
import random
from pygiftparser import parser as pygift

_ = pygift.i18n.language.gettext

######################################
##              Parser              ##
######################################

def parseFile(f):
    """
    parse a file to transform a text in GIFT format to an list of questions
    """
    cleanedSource = fullSource = ""
    category='$course$'
    newCategory = None
    questions=[]

    for  line in f:
        if pygift.reSepQuestions.match(line):
            if newCategory:
                # the previous line was a category declaration
                category = newCategory
                newCategory = None
            else:
                if cleanedSource != "":
                    # this is the end of a question
                    questions.append(Question(cleanedSource,fullSource,category))
                cleanedSource = fullSource = ""
        else:
            # it is not a blank line : is it a category definition?
            match = pygift.reCategory.match(line)
            if match:
                newCategory = match.group('cat')
                continue

            # is it a comment ?
            if not pygift.reComment.match(line):
                cleanedSource += line
            fullSource+=line

    if cleanedSource != "":
        questions.append(Question(cleanedSource,fullSource,category))

    return questions


######################################
##           Question               ##
######################################
class Question(pygift.Question):
    def __init__(self,source,full,cat):
        pygift.Question.__init__(self,source,full,cat)

    def toEDX(self):
        """
        produces an XML fragment for EDX
        """
        if not self.valid :
            logging.warning (pygift.INVALID_FORMAT_QUESTION ) #
            return ''
        return self.answers.toEDX()


    def parse(self,source):
        """ parses a question source. Comments should be removed first"""
        # split according to the answer
        match = pygift.reAnswer.match(source)
        if not match:
            # it is a description
            self.answers = Description(self)
            self._parseHead(source)
        else:
            self.tail=pygift.stripMatch(match,'tail')
            self._parseHead(match.group('head'))
            self.generalFeedback = pygift.stripMatch(match,'generalfeedback')
            # replace \n
            self.generalFeedback = re.sub(r'\\n','\n',self.generalFeedback)
            self._parseAnswer(match.group('answer'))


    def _parseNumericText(self,text):
        m = pygift.reAnswerNumericInterval.match(text)
        if m :
            a = NumericAnswerMinMax(m)
        else :
            m = pygift.reAnswerNumericValue.match(text)
            if m:
                a = NumericAnswer(m)
            else :
                self.valid = False
                return None
        a.feedback = pygift.stripMatch(m,"feedback")
        return a

    def _parseNumericAnswers(self,answer):
        self.numeric = True;
        answers=[]
        for match in pygift.reAnswerMultipleChoices.finditer(answer):
            a = self._parseNumericText(match.group('answer'))
            if not a:
                return
            # fractions
            if match.group('fraction') :
                a.fraction=float(match.group('fraction'))
            else:
                if match.group('sign') == "=":
                    a.fraction = 100
                else:
                    a.fraction = 0
            a.feedback = pygift.stripMatch(match,"feedback")
            answers.append(a)
        if len(answers) == 0:
            a = self._parseNumericText(answer)
            if a:
                a.fraction=100
                answers.append(a)
        self.answers = NumericAnswerSet(self,answers)


    def _parseAnswer(self,answer):
        # Essay
        if answer=='':
            self.answers = Essay(self)
            return

        # True False
        match = pygift.reAnswerTrueFalse.match(answer)
        if match:
            self.answers = TrueFalseSet(self,match)
            return

        # Numeric answer
        if pygift.reAnswerNumeric.match(answer) != None:
            self._parseNumericAnswers(answer[1:])
            return


        #  answers with choices and short answers
        answers=[]
        select = False
        short = True
        matching = True
        for match in pygift.reAnswerMultipleChoices.finditer(answer):
            a = AnswerInList(match)
            # one = sign is a select question
            if a.select: select = True
            # short answers are only = signs without fractions
            short = short and a.select and a.fraction == 100
            matching = matching and short and a.isMatching
            answers.append(a)

        if len(answers) > 0 :
            if matching:
                self.answers = MatchingSet(self,answers)
                self.valid = self.answers.checkValidity()
            elif short:
                self.answers = ShortSet(self,answers)
            elif select:
                self.answers = SelectSet(self,answers)
            else:
                self.answers = MultipleChoicesSet(self,answers)
                self.valid = self.answers.checkValidity()
        else:
            # not a valid question  ?
            logging.warning (pygift.INVALID_FORMAT_QUESTION+' '+self.full)
            self.valid = False

######################################
##             Answer               ##
######################################

class AnswerSet(pygift.AnswerSet):
    def __init(self,question):
        pygift.AnswerSet.__init__(self,question)
        self.max_att = '1'

#IMS
    def listInteractionsIMS(self,doc,tag,text):
        pass

    def possiblesAnswersIMS(self,doc,tag,text, rcardinality='Single'):
        with doc.tag('response_str', rcardinality=rcardinality, ident='response_'+str(self.question.id)):
            doc.stag('render_fib', rows=5, prompt='Box', fibtype="String")

    def toIMSFB(self,doc,tag,text):
        pass


#EDX
    def toEDX(self):
        assert (self.question)
        doc = yattag.Doc()
        with doc.tag("problem", display_name=self.question.title, max_attempts=self.max_att):
            with doc.tag("legend"):
                pygift.mdToHtml(self.question.text,doc)
            self.scriptEDX(doc)
            self.ownEDX(doc)
            # FIXME : Ajouter un warning ici si rien n'est renvoyé
            if (len(self.question.generalFeedback) > 1):
                with doc.tag("solution"):
                    with doc.tag("div", klass="detailed-solution"):
                        pygift.mdToHtml(self.question.generalFeedback,doc)
        return doc.getvalue()

    def ownEDX(self,doc):
        pass

    def scriptEDX(self,doc):
        pass

class Essay(pygift.Essay, AnswerSet):
    def __init__(self,question):
        pygift.Essay.__init__(self,question)
        AnswerSet.__init__(self,question)
        self.max_att = ''

    def scriptEDX(self,doc):
        with doc.tag("script", type="loncapa/python"):
            doc.text("""
import re
def checkAnswerEssay(expect, ans):
    response = re.search('', ans)
    if response:
        return 1
    else:
        return 0
            """)
        doc.asis('<span id="'+str(self.question.id)+'"></span>')
        with doc.tag("script", type="text/javascript"):
            doc.asis("""
    /* The object here is to replace the single line input with a textarea */
    (function() {
    var elem = $("#"""+str(self.question.id)+"""")
        .closest("div.problem")
        .find(":text");
    /* There's CSS in the LMS that controls the height, so we have to override here */
    var textarea = $('<textarea style="height:150px" rows="20" cols="70"/>');
    console.log(elem);
    console.log(textarea);
    //This is just a way to do an iterator in JS
    for (attrib in {'id':null, 'name':null}) {
        textarea.attr(attrib, elem.attr(attrib));
    }
    /* copy over the submitted value */
    textarea.val(elem.val())
    elem.replaceWith(textarea);

    })();
            """)

    def ownEDX(self,doc):
        with doc.tag("customresponse", cfn="checkAnswerEssay"):
            doc.asis('<textline size="40" correct_answer="" label="Problem Text"/>')

class Description(pygift.Description, AnswerSet):
    def __init__(self,question):
        pygift.Description.__init__(self,question)
        AnswerSet.__init__(self,question)
        self.cc_profile = 'DESCRIPTION'

class TrueFalseSet(pygift.TrueFalseSet, AnswerSet):
    def __init__(self,question,match):
        pygift.TrueFalseSet.__init__(self,question,match)
        AnswerSet.__init__(self,question)
        self.cc_profile = 'TRUEFALSE'

    def ownEDX(self, doc):
        with doc.tag("multiplechoiceresponse"):
            with doc.tag("choicegroup", type="MultipleChoice"):
                if self.answer :
                    correct = 'true'
                    wrong = 'false'
                else :
                    correct = 'false'
                    wrong = 'true'
                with doc.tag("choice", correct=correct):
                    doc.text(_('True'))
                    if correct == 'true':
                        doc.asis("<choicehint>"+self.feedbackCorrect+"</choicehint>")
                    else :
                        doc.asis("<choicehint>"+self.feedbackWrong+"</choicehint>")
                with doc.tag("choice", correct=wrong):
                    doc.text(_('False'))
                    if wrong == 'true':
                        doc.asis("<choicehint>"+self.feedbackCorrect+"</choicehint>")
                    else :
                        doc.asis("<choicehint>"+self.feedbackWrong+"</choicehint>")

    def possiblesAnswersIMS(self,doc,tag,text):
        with tag('response_lid', rcardinality='Single', ident='response_'+str(self.question.id)):
            with tag('render_choice', shuffle='No'):
                with tag('response_label', ident='answer_'+str(self.question.id)+'_'+'0'):
                    with tag('material'):
                        with tag('mattext', texttype="text/html"):
                            text(_('True'))
                with tag('response_label', ident='answer_'+str(self.question.id)+'_'+'1'):
                    with tag('material'):
                        with tag('mattext', texttype="text/html"):
                            text(_('False'))


    def listInteractionsIMS(self,doc,tag,text):
            score = 0
            if self.answer :
                title1 = 'Correct'
                score1 = 100
                title2 = ''
                score2 = 0
            else :
                title1 = ''
                score1 = 0
                title2 = 'Correct'
                score2 = 100
            with tag('respcondition', title=title1):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                        text('answer_'+str(self.question.id)+'_0')
                with tag('setvar', varname='SCORE', action='Set'):
                    text(score1)
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_0')
            with tag('respcondition', title=title2):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                        text('answer_'+str(self.question.id)+'_1')
                with tag('setvar', varname='SCORE', action='Set'):
                    text(score2)
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_1')


class NumericAnswerSet(pygift.NumericAnswerSet, AnswerSet):
    """
    """
    def __init__(self,question,answers):
        pygift.NumericAnswerSet.__init__(self, question, answers)
        AnswerSet.__init__(self, question)

    def ownEDX(self,doc):
        #FIXME : Problème pour le multi answer NUMERIC, ne gère qu'une réponse
        correctAnswer = []
        for a in self.answers:
            if a.fraction > 0:
                correctAnswer.append(a)
        if len(correctAnswer) == 0:
            logging.warning('')
            return
        elif len(correctAnswer) == 1:
            correctAnswer[0].ownEDX(doc)

class MatchingSet(pygift.MatchingSet, AnswerSet):
    """  a mapping (list of pairs) """
    def __init__(self,question,answers):
        pygift.MatchingSet.__init__(self, question, answers)
        AnswerSet.__init__(self, question)

    def ownEDX(self,doc):
        for a in self.answers:
            with doc.tag('h2'):
                doc.text(a.question+" ")
            with doc.tag('optionresponse'):
                options = '\"('
                random.shuffle(self.possibleAnswers)
                for a2 in self.possibleAnswers:
                    options += "'"+a2+"'"+','
                options += ')\"'
                doc.asis("<optioninput label=\""+a.question+"\" options="+options+"  correct=\""+a.answer+"\" ></optioninput>")

class ChoicesSet(pygift.ChoicesSet, AnswerSet):
    def __init__(self,question,answers):
        pygift.ChoicesSet.__init__(self, question, answers)
        AnswerSet.__init__(self, question)

#IMS
    def listInteractionsIMS(self,doc,tag,text):
        for id_a, answer in enumerate(self.answers):
            score = 0
            if answer.fraction == 100:
                title = 'Correct'
                score = 100
            else:
                title = ''
                score = answer.fraction
            with tag('respcondition', title=title):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                        text('answer_'+str(self.question.id)+'_'+str(id_a))
                with tag('setvar', varname='SCORE', action='Set'):
                    text(score)
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))

    def possiblesAnswersIMS(self,doc,tag,text,rcardinality='Single'):
        with tag('response_lid', rcardinality=rcardinality, ident='response_'+str(self.question.id)):
            with tag('render_choice', shuffle='No'):
                for id_a, answer in enumerate(self.answers):
                    with tag('response_label', ident='answer_'+str(self.question.id)+'_'+str(id_a)):
                        with tag('material'):
                            with tag('mattext', texttype="text/html"):
                                text(pygift.markupRendering(answer.answer,self.question.markup))

    def toIMSFB(self,doc,tag,text):
        for id_a, answer in enumerate(self.answers):
            with tag('itemfeedback', ident='feedb_'+str(id_a)):
                with tag('flow_mat'):
                    with tag('material'):
                        with tag('mattext', texttype='text/html'):
                            if answer.feedback:
                                text(pygift.markupRendering(answer.feedback,self.question.markup))
                            else :
                                text('')

class ShortSet(pygift.ShortSet, ChoicesSet):

    def __init__(self,question,answers):
        pygift.ShortSet.__init__(self, question, answers)
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MISSINGWORD'

    def ownEDX(self,doc):
        with doc.tag('stringresponse', answer = self.answers[0].answer, type = 'ci'):
            if len(self.answers) > 1:
                for i,a in enumerate(self.answers):
                    if i > 0 :
                        doc.asis('<additional_answer answer="'+ a.answer +'"></additional_answer>')
            doc.asis("<textline size='20' />")

class SelectSet(pygift.SelectSet, ChoicesSet):
    """ One  choice in a list"""
    def __init__(self,question,answers):
        pygift.SelectSet.__init__(self, question, answers)
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MULTICHOICE'

    def ownEDX(self,doc):
        with doc.tag("multiplechoiceresponse"):
            with doc.tag("choicegroup", type="MultipleChoice"):
                for a in self.answers:
                    if a.fraction>0:
                        korrect = 'true'
                    else :
                        korrect = 'false'
                    with doc.tag("choice", correct=korrect):
                        doc.text(a.answer)
                        if (a.feedback) and (len(a.feedback)> 1):
                            doc.asis("<choicehint>"+a.feedback+"</choicehint>")

class MultipleChoicesSet(pygift.MultipleChoicesSet, ChoicesSet):
    """ One or more choices in a list"""
    def __init__(self,question,answers):
        pygift.MultipleChoicesSet.__init__(self, question, answers)
        ChoicesSet.__init__(self,question,answers)
        self.cc_profile = 'MULTIANSWER'

    def ownEDX(self,doc):
        with doc.tag("choiceresponse", partial_credit="EDC"):
            with doc.tag("checkboxgroup"):
                for a in self.answers:
                    if a.fraction>0:
                        korrect = 'true'
                    else :
                        korrect = 'false'
                    with doc.tag("choice", correct=korrect):
                        doc.text(a.answer)
                        if (a.feedback) and (len(a.feedback)> 1):
                            with doc.tag("choicehint", selected="true"):
                                doc.text(a.answer+" : "+a.feedback)

    def possiblesAnswersIMS(self,doc,tag,text):
        ChoicesSet.possiblesAnswersIMS(self,doc,tag,text,'Multiple')

    def listInteractionsIMS(self,doc,tag,text):
        with tag('respcondition', title="Correct", kontinue='No'):
            with tag('conditionvar'):
                with tag('and'):
                    for id_a, answer in enumerate(self.answers):
                        score = 0
                        try:
                            score = answer.fraction
                        except:
                            pass
                        if score <= 0:
                            with tag('not'):
                                with tag('varequal', case='Yes', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                                    text('answer_'+str(self.question.id)+'_'+str(id_a))
                        else:
                            with tag('varequal', case='Yes', respident='response_'+str(self.question.id)): # respoident is id of response_lid element
                                text('answer_'+str(self.question.id)+'_'+str(id_a))
            with tag('setvar', varname='SCORE', action='Set'):
                text('100')
            doc.stag('displayfeedback', feedbacktype='Response', linkrefid='general_fb')
        for id_a, answer in enumerate(self.answers):
            with tag('respcondition', kontinue='No'):
                with tag('conditionvar'):
                    with tag('varequal', respident='response_'+str(self.question.id), case="Yes"):
                        text('answer_'+str(self.question.id)+'_'+str(id_a))
                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))


################# Single answer ######################
class Answer(pygift.Answer):
    """ one answer in a list"""
    pass

class NumericAnswer(pygift.NumericAnswer, Answer):
    def __init__(self,match):
        pygift.NumericAnswer.__init__(self,match)

    def ownEDX(self, doc):
        with doc.tag('numericalresponse', answer = str(self.value)):
            if self.tolerance != 0.0:
                doc.asis("<responseparam type='tolerance' default='"+str(self.tolerance)+"' />")
            doc.asis("<formulaequationinput />")

class NumericAnswerMinMax(pygift.NumericAnswerMinMax, Answer):
    def __init__(self,match):
        pygift.NumericAnswerMinMax.__init__(self,match)

    def ownEDX(self, doc):
        with doc.tag('numericalresponse', answer = "["+str(self.mini)+","+str(self.maxi)+"]"):
            doc.asis("<formulaequationinput />")

class AnswerInList(pygift.AnswerInList, Answer):
    def __init__(self,match):
        pygift.AnswerInList.__init__(self,match)

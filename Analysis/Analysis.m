% Analysis for psychometric function


%addpath('/NOBACKUP2/Pred_spec/Palamedes')


%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ntrialseachcond = 27*2;
sessiontype = 2; % 1 type, 2 location





nlevels = 5;
% extract data


% Trial types

% Expectation / Pain type presented
% trial numbers which would be expected for a full expt with all blocks completed...

% 1 {'ThermalHigh_thermal'} - 12 trials-pt
% 2 {'ThermalHigh_mechano'} - 6 trials-pt
% 3 {'MechanoHigh_mechano'} - 12 trials-pt
% 4 {'MechanoHigh_thermal'} - 6 trials-pt
% 5 {'Noexpect_thermal'} - 9 trials-pt
% 6 {'Noexpect_mechano'} - 9 trials-pt


% 1 {'LeftHigh_Left'} - 12 trials-pt
% 2 {'LeftHigh_Right'} - 6 trials-pt
% 3 {'RightHigh_Right'} - 12 trials-pt
% 4 {'RightHigh_Left'} - 6 trials-pt
% 5 {'Noexpect_Left'} - 9 trials-pt
% 6 {'Noexpect_Right'} - 9 trials-pt
% 


% Can analyse thermal and mechano irrespective of expectation condition
% so cond 1 = thermal (1, 4, 5)
% cond 2 = mechano (2, 3, 6)




session1 = [48.4580678851175, ...
49.144316797215, ...
49.8305657093124, ...
50.5168146214099, ...
51.2030635335074];

session2 = [48.7086369834031, ...
49.6354553575626, ...
50.5622737317222, ...
51.4890921058818, ...
52.4159104800414
];

%datapsychophys2thermsW30PainType20210722T14
%levels = [48.5 49.4 50.3 51.3 52.2];
%dataTestingPainLocW30PainLocation20210802T17
%levels = [47.2 47.9 48.6 49.3 50.0];

%levels debug
%levels = [15, 25, 40, 45, 50];
%levels = [40, 42, 44, 46, 48, 50, 52, 54, 56];


%extract temperature levels of the current dataset
levels = sort(unique(data.ComparisonIntensity))

comparison_intensity_thermal = round(levels,1)

comparison_intensity_mechano =  [32, 64, 128, 256, 512]


%conditions_all_expects = nan(2,ntrialseachcond,5);



%conditions = nan(5,ntrialseachcond,5);
tmp = [];
results = nan(5,1,2);
for condition = 1:2; %conditions
%     conditions(:,i) = find(subjectdata(:,1) == i); %find all intact trials, all BS trials...
%     tmp(:,i) = find(subjectdata(:,1) == i);
    for intensity = 1:nlevels %intensity
%       SFs(:,j) = find(subjectdata(:,2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         tmp2(:,j) = find(subjectdata(:,2) == j);
%         subjectdata(tmp,tmp2)

        if condition == 1 %thermal / left
            
            % Count responses
            tmpresp = find( ... 
                ( (data.TrialTypeID == 1) | (data.TrialTypeID == 4) | (data.TrialTypeID == 5) ) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
            data.SubRespComparisonMorePain == 1    ); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
            
           
            
            
            
            % Count the total N of trials of this type
            tmptotal = find( ... 
                ( (data.TrialTypeID == 1) | (data.TrialTypeID == 4) | (data.TrialTypeID == 5) ) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)  ); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
            
        else % mechano / right
            if sessiontype == 1 % Pain Type session, so we need mechanical intensities used
                
                
                % Count responses
                tmpresp = find( ...
                ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
             
                % Count the total N of trials of this type
                tmptotal = find( ...
                ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity) ); % find condition 2, 3 or 6 where comparison intensity is the required one
             
            else % location session, only thermal intensities for now
                 % Count responses 
                 tmpresp = find( ...
                 ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                  data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                  data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
              
                % Count the total N of trials of this type
                tmptotal = find( ...
                 ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                  data.ComparisonIntensity == comparison_intensity_thermal(intensity) ); % find condition 2, 3 or 6 where comparison intensity is the required one
                 % and the response was 1, meaning comparison more pain
             end
                
        end
        
        
        
        
        %(:,2) == j) & (subjectdata(:,1) == i) & subjectdata(:,3) == 2)';
%         conditions(j,:,i) = tmp;
        results(intensity,1,condition) = size(tmpresp,1); %subs response count comparison = more pain
        results(intensity,2,condition) = size(tmptotal,1); %total number of trials in that condition
        %results(n, 1, m) / results(n, 2, m) * 100 = % score
        

    end
end
results %print results


%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% figure
ntrialseachcond = max(reshape(results, 20, 1, 1)); % just take the max n of trials for any condition, we simply
% need a rough number for graph axes here

figure; plot(1:nlevels, results(1:nlevels,1,1), 'ro-') %Thermal
hold on;
plot(1:nlevels, results(1:nlevels,1,2), 'bs-') % Mechano
%plot(1:5, results(1:5,1,3), 'go-') %occl
%plot(1:5, results(1:5,1,4), 'kx-') %del sharp
%plot(1:5, results(1:5,1,5), 'cx-') %del fuzzy
axis([0.5 nlevels+0.5 -0.5 ntrialseachcond+0.5])
if sessiontype == 1
    [leg] = legend('Thermal', 'Mechano', 'Location', 'Northwest');
elseif sessiontype == 2
    [leg] = legend('Left', 'Right', 'Location', 'Northwest');
end
ax = findobj(gcf,'type','axes'); %Retrieve the axes to be copied
hold off;

colorpoints(1) = 'r';
colorpoints(2) = 'b';
colorpoints(3) = 'g';
colorpoints(4) = 'k';
colorpoints(5) = 'c';

markershape(1) = 's';
markershape(2) = 's';
markershape(3) = 'o';
markershape(4) = 'x';
markershape(5) = 'x';



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% palamedes analysis

% Comnine condition 1 and 2, or analyse separately?
  combineconds = false;

if combineconds
    condition_for_loop = 1;
    resultsanalysis = results(:,:,1) + results(:,:,2)
else
    condition_for_loop = [1:2];
    resultsanalysis = results
end


%add path
addpath('/NOBACKUP2/Pred_spec/Palamedes') 
addpath('/data/hu_yurevina/ownCloud/pred_spec/Psychophysics_data_and_analysis/Palamedes') 

disp ('Palamedes...')
%Stimulus intensities
StimLevels = comparison_intensity_thermal'; 
figure('name','Maximum Likelihood Psychometric Function Fitting');
    axes
    hold on

for condition = condition_for_loop %conditions
    
    %Number of positive responses (e.g., 'yes' or 'correct' at each of the
    %   entries of 'StimLevels' 
    
    %Number of trials at each entry of 'StimLevels'
    %OutOfNum = [ones(1,nlevels)*ntrialseachcond];
    for i = 1:nlevels
        NumPos(i) = [resultsanalysis(i,1,condition)];
        OutOfNum(i) = [resultsanalysis(i,2,condition)];
    end
   
    
    
    
    %Use the Logistic function
    PF = @PAL_Logistic;
    %@PAL_Logistic;  %Alternatives: PAL_Gumbel, PAL_Weibull,
    %PAL_Quick, PAL_logQuick,
    %PAL_CumulativeNormal, PAL_HyperbolicSecant
    
    %Threshold and Slope are free parameters, guess and lapse rate are fixed
    paramsFree = [1 1 0 0];  %1: free parameter, 0: fixed parameter
    
    %Parameter grid defining parameter space through which to perform a
    %brute-force search for values to be used as initial guesses in iterative
    %parameter search.
    %searchGrid.alpha = 45:.01:53; %PSE
    searchGrid.alpha = 1:.01:5; %PSE for combined across subs where temp is coded 1 to 5
    searchGrid.beta = logspace(0,1,101); %slope
    searchGrid.gamma = 0.02;  %scalar here (since fixed) but may be vector %guess rate (lower asymptote)
    searchGrid.lambda = 0.02;  %ditto % lapse rate, finger error, upper asympt
    
    %Perform fit
    disp('Fitting function.....');
    [paramsValues LL exitflag] = PAL_PFML_Fit(StimLevels,NumPos, ...
        OutOfNum,searchGrid,paramsFree,PF);
    
    disp('done:')
    message = sprintf('Threshold estimate: %6.4f',paramsValues(1));
    disp(message);
    message = sprintf('Slope estimate: %6.4f\r',paramsValues(2));
    disp(message);
    
    %Create simple plot
    ProportionCorrectObserved=NumPos./OutOfNum;
    StimLevelsFineGrain=[min(StimLevels-0.05):max(StimLevels+0.05)./1000:max(StimLevels+0.05)];
    ProportionCorrectModel = PF(paramsValues,StimLevelsFineGrain);
    
    
    disp('Goodness of Fit')
    B = 1000;
    [Dev pDev DevSim converged] = PAL_PFML_GoodnessOfFit(StimLevels, NumPos, OutOfNum, paramsValues, paramsFree, B, PF,'searchGrid', searchGrid);
  
    disp(sprintf('Dev: %6.4f',Dev))
    disp(sprintf('pDev: %6.4f',pDev))
    disp(sprintf('N converged: %6.4f',sum(converged==1)))
    disp('--') %empty line
    
    
    plot(StimLevelsFineGrain,ProportionCorrectModel,'-','color',colorpoints(condition),'linewidth',2);
    plot(StimLevels,ProportionCorrectObserved,'LineStyle', 'None','Color', colorpoints(condition),'Marker',markershape(condition),'MarkerFaceColor', 'None','markersize',10);
    set(gca, 'fontsize',16);
    set(gca, 'Xtick',StimLevels);
    axis([min(StimLevels) max(StimLevels) 0 1]);
    xlabel('Stimulus Intensity');
    ylabel('P(Comparison More Pain)');
end

set(gca, 'fontsize',14);
set(gca, 'Xtick',StimLevels);
axis([min(StimLevels-0.05) max(StimLevels+0.05) 0 1]);
plot([StimLevels(1) StimLevels(5)],[0.5 0.5])
plot([StimLevels(3) StimLevels(3)], [0 1], 'LineStyle', '--')
if sessiontype == 1
    [leg] = legend('Thermal', '', 'Mechano', 'Location', 'Northwest');
    if combineconds
        [leg] = legend('Thermal + Mech', 'Location', 'Northwest');
    end
else
    [leg] = legend('Left', '', 'Right', 'Location', 'Northwest');
    if combineconds
        [leg] = legend('Left + Right', 'Location', 'Northwest');
    end
end

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ntrialseachcond = 12*1;
% extract data

nCond = 2;

% Trial types

% Expectation / Pain type presented

% 1 {'ThermalHigh_thermal'} - 12 trials-pt
% 2 {'ThermalHigh_mechano'} - 6 trials-pt
% 3 {'MechanoHigh_mechano'} - 12 trials-pt
% 4 {'MechanoHigh_thermal'} - 6 trials-pt
% 5 {'Noexpect_thermal'} - 9 trials-pt
% 6 {'Noexpect_mechano'} - 9 trials-pt
% 


% lot thermal and mechano on separate figures
% 3 conditions each
% 
whichPainType = 2; % 1 thermal/left or 2 mechano/right


% Comnine condition 1 and 2, or analyse separately?
combineconds = true;


% Keep the N trials of High and Low the same or not?
% if true then a random sample will be taken from the High trials of the
% same number as the number of low trials
equalizeNtrials = true;


conditionorderthermal = [1, 4, 5];
conditionordermechano = [3, 2, 6];



%comparison_intensity_thermal = round([48.4580678851175, 49.144316797215, 49.8305657093124, 50.5168146214099, 51.2030635335074],1)

comparison_intensity_mechano =  [32, 64, 128, 256, 512]


%conditions_all_expects = nan(2,ntrialseachcond,5);



%conditions = nan(5,ntrialseachcond,5);
tmp = [];
results = nan(nlevels,1,nCond);
for condition = 1:nCond %conditions of expectation
%     conditions(:,i) = find(subjectdata(:,1) == i); %find all intact trials, all BS trials...
%     tmp(:,i) = find(subjectdata(:,1) == i);
    for intensity = 1:nlevels %intensity
%       SFs(:,j) = find(subjectdata(:,2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         tmp2(:,j) = find(subjectdata(:,2) == j);
%         subjectdata(tmp,tmp2)
        if whichPainType == 1 %thermal / left
            
            % Count responses 
            tmpresp = find( ... 
                 (data.TrialTypeID == conditionorderthermal(condition)) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
            data.SubRespComparisonMorePain == 1    ); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
            
            
            if condition == 1
                tmpresHIGH = tmpresp;
            end
            
            
            % Count the total N of this trial type
            tmptotal = find( ... 
                 (data.TrialTypeID == conditionorderthermal(condition)) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
            
            
            if equalizeNtrials && condition == 2 % once we have processed low conditions and know
                %their total number, we need to resample the high ones
                
                % find all the high trials, regardless of response
                tmpHIGHtotal = find( ... 
                (data.TrialTypeID == conditionorderthermal(1)) & ...
                data.ComparisonIntensity == comparison_intensity_thermal(intensity)) % find condition 1, 4 or 5 where comparison intensity is the required one
               
                % take a randomsample of them with the size of the Low condition               
                samplevector = randsample(size(tmpHIGHtotal, 1), size(tmptotal, 1))
                
                tmpHIGHtotal(samplevector)
                
                % look again at the high trials where they answered
                % comparison more pain, but only in the subset defined by
                % our sample vector
                tmpresHIGHnew = find( ... 
                (data(tmpHIGHtotal(samplevector), :).TrialTypeID == conditionorderthermal(1)) & ...
                data(tmpHIGHtotal(samplevector), :).ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                data(tmpHIGHtotal(samplevector), :).SubRespComparisonMorePain == 1    ) % find condition 1, 4 or 5 where comparison intensity is the required one
                % and the response was 1, meaning comparison more pain
            
            end
            
            
            
            
        else % mechano / right
            if sessiontype == 1 %pain type session, need mechano intensities
            
             % Count responses 
                tmpresp = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
             
             % Count the total N of this trial type
                tmptotal = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity) ); % find condition 2, 3 or 6 where comparison intensity is the required one
             
            else %location session, use thermal intensities only
                
                 % Count responses 
                tmpresp = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
             
                % Count the total N of this trial type
                tmptotal = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_thermal(intensity) ); % find condition 2, 3 or 6 where comparison intensity is the required one
                % and the response was 1, meaning comparison more pain
                
                
                if equalizeNtrials && condition == 2 % once we have processed low conditions and know
                    %their total number, we need to resample the high ones
                    
                    % find all the high trials, regardless of response
                    tmpHIGHtotal = find( ...
                        (data.TrialTypeID == conditionordermechano(1)) & ...
                        data.ComparisonIntensity == comparison_intensity_thermal(intensity)) % find condition 1, 4 or 5 where comparison intensity is the required one
                    
                    % take a randomsample of them with the size of the Low condition
                    samplevector = randsample(size(tmpHIGHtotal, 1), size(tmptotal, 1))
                    
                    tmpHIGHtotal(samplevector)
                    
                    % look again at the high trials where they answered
                    % comparison more pain, but only in the subset defined by
                    % our sample vector
                    tmpresHIGHnew = find( ...
                        (data(tmpHIGHtotal(samplevector), :).TrialTypeID == conditionordermechano(1)) & ...
                        data(tmpHIGHtotal(samplevector), :).ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                        data(tmpHIGHtotal(samplevector), :).SubRespComparisonMorePain == 1    ) % find condition 1, 4 or 5 where comparison intensity is the required one
                    % and the response was 1, meaning comparison more pain
            
                 end
                
                
                
                
            end
                
        end
        
        
        
        
        %(:,2) == j) & (subjectdata(:,1) == i) & subjectdata(:,3) == 2)';
%         conditions(j,:,i) = tmp;
        if whichPainType == 1 %thermal/left
            results_thermal_left(intensity,1,condition) = size(tmpresp,1);
            results_thermal_left(intensity,2,condition) = size(tmptotal,1);
            if equalizeNtrials && condition == 2
                results_thermal_left(intensity,1,1) = size(tmpresHIGHnew,1);
                results_thermal_left(intensity,2,1) = size(tmptotal,1);
            end
        elseif whichPainType == 2 %mechano/right
            results_mechano_right(intensity,1,condition) = size(tmpresp,1);
            results_mechano_right(intensity,2,condition) = size(tmptotal,1);
            if equalizeNtrials && condition == 2
                results_mechano_right(intensity,1,1) = size(tmpresHIGHnew,1);
                results_mechano_right(intensity,2,1) = size(tmptotal,1);
            end
        end
    end
end

% Comnine condition 1 and 2, or analyse separately?
if combineconds
    
    results = results_thermal_left + results_mechano_right
  
else
    if whichPainType == 1
        results = results_thermal_left
    elseif whichPainType == 2
        results = results_mechano_right
    end
end


%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ntrialseachcond = max(reshape(results, 20, 1, 1)); % just take the max n of trials for any condition, we simply
% need a rough number for graph axes here

% figure
figure; plot(1:nlevels, results(1:nlevels,1,1), 'ro-') %Thermal
hold on;
plot(1:nlevels, results(1:nlevels,1,2), 'bs-') % Mechano
%plot(1:nlevels, results(1:nlevels,1,3), 'go-') %occl
%plot(1:5, results(1:5,1,4), 'kx-') %del sharp
%plot(1:5, results(1:5,1,5), 'cx-') %del fuzzy
axis([0.5 nlevels+0.5 -0.5 ntrialseachcond+0.5])
[leg] = legend('High', 'Low', 'None', 'Northwest');
ax = findobj(gcf,'type','axes'); %Retrieve the axes to be copied
hold off;

colorpoints(1) = 'r';
colorpoints(2) = 'b';
colorpoints(3) = 'g';
colorpoints(4) = 'k';
colorpoints(5) = 'c';

markershape(1) = 's';
markershape(2) = 's';
markershape(3) = 'o';
markershape(4) = 'x';
markershape(5) = 'x';



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% palamedes analysis



multiplier = 2; % for multiple sessions, need to mult the n of trials

disp ('Palamedes...')
%Stimulus intensities
StimLevels = comparison_intensity_thermal'; 
figure('name','Maximum Likelihood Psychometric Function Fitting');
    axes
    hold on

for condition = 1:2 %conditions
    
    
    switch condition
        case 1
            %ntrialseachcond = 12*multiplier;
        case 2
            %ntrialseachcond = 6*multiplier;
        case 3
            %ntrialseachcond = 9*multiplier;
    end
    
    
    %Number of positive responses (e.g., 'yes' or 'correct' at each of the
    %   entries of 'StimLevels'
    for i = 1:nlevels
        NumPos(i) = [results(i,1,condition)];
        OutOfNum(i) = [results(i,2,condition)];
    end
    %Number of trials at each entry of 'StimLevels'
    %OutOfNum = ones(1,nlevels)*ntrialseachcond;
    
    
    %Use the Logistic function
    PF = @PAL_Logistic;
    %@PAL_Logistic;  %Alternatives: PAL_Gumbel, PAL_Weibull,
    %PAL_Quick, PAL_logQuick,
    %PAL_CumulativeNormal, PAL_HyperbolicSecant
    
    %Threshold and Slope are free parameters, guess and lapse rate are fixed
    paramsFree = [1 1 0 0];  %1: free parameter, 0: fixed parameter
    
    %Parameter grid defining parameter space through which to perform a
    %brute-force search for values to be used as initial guesses in iterative
    %parameter search.
    searchGrid.alpha = 45:.01:53; %PSE
    %searchGrid.alpha = 1:.01:5; %PSE for combined across subs where temp is coded 1 to 5
    searchGrid.beta = logspace(0,1,101); %slope
    searchGrid.gamma = 0.02;  %scalar here (since fixed) but may be vector %guess rate (lower asymptote)
    searchGrid.lambda = 0.02;  %ditto % lapse rate, finger error, upper asympt
    
    %Perform fit
    disp('Fitting function.....');
    [paramsValues LL exitflag] = PAL_PFML_Fit(StimLevels,NumPos, ...
        OutOfNum,searchGrid,paramsFree,PF);
    
    disp('done:')
    message = sprintf('Threshold estimate: %6.4f',paramsValues(1));
    disp(message);
    message = sprintf('Slope estimate: %6.4f\r',paramsValues(2));
    disp(message);
    
    %Create simple plot
    ProportionCorrectObserved=NumPos./OutOfNum;
    StimLevelsFineGrain=[min(StimLevels-0.05):max(StimLevels+0.05)./1000:max(StimLevels+0.05)];
    ProportionCorrectModel = PF(paramsValues,StimLevelsFineGrain);
    
    
    disp('Goodness of Fit')
    B = 1000;
    [Dev pDev DevSim converged] = PAL_PFML_GoodnessOfFit(StimLevels, NumPos, OutOfNum, paramsValues, paramsFree, B, PF,'searchGrid', searchGrid);
  
    disp(sprintf('Dev: %6.4f',Dev))
    disp(sprintf('pDev: %6.4f',pDev))
    disp(sprintf('N converged: %6.4f',sum(converged==1)))
    disp('--') %empty line
    
    
    plot(StimLevelsFineGrain,ProportionCorrectModel,'-','color',colorpoints(condition),'linewidth',2);
    plot(StimLevels,ProportionCorrectObserved,'LineStyle', 'None','Color', colorpoints(condition),'Marker',markershape(condition),'MarkerFaceColor', 'None','markersize',10);
    set(gca, 'fontsize',16);
    set(gca, 'Xtick',StimLevels);
    axis([min(StimLevels) max(StimLevels) 0 1]);
    xlabel('Stimulus Intensity');
    ylabel('P(Comparison More Pain)');
end

set(gca, 'fontsize',14);
set(gca, 'Xtick',StimLevels);
axis([min(StimLevels-0.05) max(StimLevels+0.05) 0 1]);
plot([0 5],[0.5 0.5])
plot([0.3 0.3], [0 1], 'LineStyle', '--')
[leg] = legend('High', '', 'Low', '', 'None', 'Location', 'Northwest');

%% Combine data from several subjects

if not(exist('data_everyone', 'var'))
    data_everyone = [];
end

%extract temperature levels of the current dataset
levels = sort(unique(data_all.ComparisonIntensity))

datatmp = data_all;
for i = 1:5
    tmp = find(data_all.ComparisonIntensity == levels(i));
    datatmp.ComparisonIntensity(tmp, :) = i;
end
data_everyone = [data_everyone; datatmp];
size(data_everyone)



%% RT analysis for Left/Right expectation

conditionorderthermal = [1, 4, 5];
conditionordermechano = [3, 2, 6];


for condition = 1:2 %conditions of expectation
    % left
    tmpRT = find( (data.TrialTypeID == conditionorderthermal(condition)));
    
    if condition == 1
        RTleftHIGH = data.RTs(tmpRT,:);
    elseif condition == 2
        RTleftLOW = data.RTs(tmpRT,:);
    end
    
    % right
    tmpRT = find( (data.TrialTypeID == conditionordermechano(condition)));
    
    if condition == 1
        RTrightHIGH = data.RTs(tmpRT,:);
    elseif condition == 2
        RTrightLOW = data.RTs(tmpRT,:);
    end
   
    
    
end
RTsHIGH = [RTleftHIGH; RTrightHIGH];
RTsLOW = [RTleftLOW; RTrightLOW];

median(RTsHIGH)
median(RTsLOW)
mean(RTsHIGH)
mean(RTsLOW)